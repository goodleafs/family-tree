from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional, Dict, Any
from datetime import date
from app.models import Person, Relationship, Family
from app.schemas import PersonCreate, PersonUpdate, RelationshipCreate, RelationshipUpdate

class PersonService:
    @staticmethod
    async def get_person_by_id(db: AsyncSession, person_id: int) -> Optional[Person]:
        """根据ID获取成员"""
        result = await db.execute(select(Person).where(Person.id == person_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_persons_by_family(
        db: AsyncSession,
        family_id: int,
        skip: int = 0,
        limit: int = 50,
        search: Optional[str] = None,
        generation: Optional[int] = None
    ) -> tuple[List[Person], int]:
        """获取家族成员列表"""
        query = select(Person).where(Person.family_id == family_id)
        count_query = select(func.count(Person.id)).where(Person.family_id == family_id)
        
        # 搜索过滤
        if search:
            search_filter = Person.name.contains(search)
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)
        
        # 世代过滤
        if generation is not None:
            gen_filter = Person.generation_number == generation
            query = query.where(gen_filter)
            count_query = count_query.where(gen_filter)
        
        # 获取总数
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # 分页和排序
        query = query.order_by(Person.generation_number, Person.birth_date).offset(skip).limit(limit)
        result = await db.execute(query)
        persons = result.scalars().all()
        
        return list(persons), total
    
    @staticmethod
    async def create_person(db: AsyncSession, person_data: PersonCreate, created_by: int) -> Person:
        """创建成员"""
        db_person = Person(
            family_id=person_data.family_id,
            name=person_data.name,
            gender=person_data.gender,
            birth_date=person_data.birth_date,
            death_date=person_data.death_date,
            birthplace=person_data.birthplace,
            residence=person_data.residence,
            occupation=person_data.occupation,
            education=person_data.education,
            biography=person_data.biography,
            achievements=person_data.achievements,
            photo_url=person_data.photo_url,
            branch_name=person_data.branch_name,
            generation_number=person_data.generation_number,
            created_by=created_by
        )
        db.add(db_person)
        await db.flush()
        return db_person
    
    @staticmethod
    async def update_person(db: AsyncSession, person: Person, update_data: PersonUpdate | dict) -> Person:
        """更新成员信息"""
        # 支持字典或 Pydantic 模型
        if isinstance(update_data, dict):
            update_dict = update_data
        else:
            update_dict = update_data.model_dump(exclude_unset=True)
        
        for field, value in update_dict.items():
            setattr(person, field, value)
        await db.flush()
        return person
    
    @staticmethod
    async def delete_person(db: AsyncSession, person: Person) -> None:
        """删除成员"""
        await db.delete(person)
        await db.flush()
    
    @staticmethod
    async def create_relationship(db: AsyncSession, rel_data: RelationshipCreate) -> Relationship:
        """创建亲属关系"""
        db_rel = Relationship(
            person_id=rel_data.person_id,
            relative_id=rel_data.relative_id,
            relation_type=rel_data.relation_type,
            is_primary=rel_data.is_primary,
            marriage_date=rel_data.marriage_date,
            divorce_date=rel_data.divorce_date
        )
        db.add(db_rel)
        
        # 如果是配偶关系，创建反向关系
        if rel_data.relation_type == "spouse":
            reverse_rel = Relationship(
                person_id=rel_data.relative_id,
                relative_id=rel_data.person_id,
                relation_type="spouse",
                is_primary=rel_data.is_primary,
                marriage_date=rel_data.marriage_date,
                divorce_date=rel_data.divorce_date
            )
            db.add(reverse_rel)
        
        await db.flush()
        return db_rel
    
    @staticmethod
    async def get_relationships(db: AsyncSession, person_id: int) -> List[Relationship]:
        """获取成员的所有关系"""
        result = await db.execute(
            select(Relationship).where(Relationship.person_id == person_id)
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def get_relationship_by_id(db: AsyncSession, relationship_id: int) -> Optional[Relationship]:
        """根据ID获取关系"""
        result = await db.execute(select(Relationship).where(Relationship.id == relationship_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def update_relationship(db: AsyncSession, relationship: Relationship, update_data: RelationshipUpdate) -> Relationship:
        """更新亲属关系"""
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(relationship, field, value)
        
        if relationship.relation_type == "spouse":
            reverse_rel = await db.execute(
                select(Relationship).where(
                    and_(
                        Relationship.person_id == relationship.relative_id,
                        Relationship.relative_id == relationship.person_id,
                        Relationship.relation_type == "spouse"
                    )
                )
            )
            reverse = reverse_rel.scalar_one_or_none()
            if reverse:
                for field, value in update_dict.items():
                    setattr(reverse, field, value)
        
        await db.flush()
        return relationship
    
    @staticmethod
    async def delete_relationship(db: AsyncSession, relationship: Relationship) -> None:
        """删除亲属关系"""
        if relationship.relation_type == "spouse":
            reverse_rel = await db.execute(
                select(Relationship).where(
                    and_(
                        Relationship.person_id == relationship.relative_id,
                        Relationship.relative_id == relationship.person_id,
                        Relationship.relation_type == "spouse"
                    )
                )
            )
            reverse = reverse_rel.scalar_one_or_none()
            if reverse:
                await db.delete(reverse)
        
        await db.delete(relationship)
        await db.flush()
    
    @staticmethod
    async def build_family_tree(
        db: AsyncSession,
        root_person_id: int,
        max_generations: int = 10
    ) -> Optional[Dict[str, Any]]:
        """构建家谱树"""
        root = await PersonService.get_person_by_id(db, root_person_id)
        if not root:
            return None
        
        visited = set()
        
        async def build_node(person: Person, generation: int) -> Dict[str, Any]:
            if person.id in visited or generation > max_generations:
                return None
            
            visited.add(person.id)
            
            node = {
                "id": person.id,
                "name": person.name,
                "gender": person.gender,
                "birth_date": person.birth_date.isoformat() if person.birth_date else None,
                "death_date": person.death_date.isoformat() if person.death_date else None,
                "photo_url": person.photo_url,
                "generation_number": person.generation_number,
                "children": [],
                "spouses": []
            }
            
            # 获取所有关系
            relationships = await PersonService.get_relationships(db, person.id)
            
            for rel in relationships:
                relative = await PersonService.get_person_by_id(db, rel.relative_id)
                if not relative or relative.id in visited:
                    continue
                
                if rel.relation_type == "child":
                    # 当前人是父母，relative是孩子
                    child_node = await build_node(relative, generation + 1)
                    if child_node:
                        node["children"].append(child_node)
                elif rel.relation_type == "spouse":
                    spouse_node = {
                        "id": relative.id,
                        "name": relative.name,
                        "gender": relative.gender,
                        "birth_date": relative.birth_date.isoformat() if relative.birth_date else None,
                        "photo_url": relative.photo_url
                    }
                    node["spouses"].append(spouse_node)
            
            return node
        
        tree = await build_node(root, 1)
        
        # 计算统计信息
        total_members = len(visited)
        max_gen = 1
        
        def count_generations(node: Dict, current_gen: int):
            nonlocal max_gen
            max_gen = max(max_gen, current_gen)
            for child in node.get("children", []):
                count_generations(child, current_gen + 1)
        
        if tree:
            count_generations(tree, 1)
        
        return {
            "root": tree,
            "total_generations": max_gen,
            "total_members": total_members
        }
