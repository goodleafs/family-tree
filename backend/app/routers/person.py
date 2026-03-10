from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from app.database import get_db
from app.schemas import (
    PersonCreate, PersonUpdate, PersonResponse, PersonListResponse,
    RelationshipCreate, RelationshipUpdate, RelationshipResponse, FamilyTreeResponse
)
from app.services import PersonService, FamilyService
from app.routers.auth import get_current_active_user
from app.utils import save_upload_file, delete_file

router = APIRouter(prefix="/persons", tags=["成员管理"])

@router.get("/family/{family_id}", response_model=PersonListResponse)
async def list_family_persons(
    family_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query(None),
    generation: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: Optional = Depends(get_current_active_user)
):
    """获取家族成员列表"""
    # 检查家族是否存在和访问权限
    family = await FamilyService.get_family_by_id(db, family_id)
    if not family:
        raise HTTPException(status_code=404, detail="家族不存在")
    
    if not family.is_public:
        if not current_user:
            raise HTTPException(status_code=403, detail="该家族为私密家族")
        role = await FamilyService.get_user_role_in_family(db, family_id, current_user.id)
        if not role:
            raise HTTPException(status_code=403, detail="您没有权限访问此家族")
    
    persons, total = await PersonService.get_persons_by_family(
        db, family_id, skip=skip, limit=limit, search=search, generation=generation
    )
    
    return {"total": total, "items": persons}

@router.get("/{person_id}", response_model=PersonResponse)
async def get_person(
    person_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Optional = Depends(get_current_active_user)
):
    """获取成员详情"""
    person = await PersonService.get_person_by_id(db, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="成员不存在")
    
    # 检查访问权限
    family = await FamilyService.get_family_by_id(db, person.family_id)
    if not family.is_public:
        if not current_user:
            raise HTTPException(status_code=403, detail="该家族为私密家族")
        role = await FamilyService.get_user_role_in_family(db, person.family_id, current_user.id)
        if not role:
            raise HTTPException(status_code=403, detail="您没有权限访问此成员")
    
    return person

@router.post("", response_model=PersonResponse, status_code=status.HTTP_201_CREATED)
async def create_person(
    person_data: PersonCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """创建成员"""
    family = await FamilyService.get_family_by_id(db, person_data.family_id)
    if not family:
        raise HTTPException(status_code=404, detail="家族不存在")
    
    is_superuser = await FamilyService.is_superuser(db, current_user.id)
    role = await FamilyService.get_user_role_in_family(db, person_data.family_id, current_user.id)
    
    if not is_superuser and not role:
        raise HTTPException(status_code=403, detail="您没有权限在此家族添加成员")
    
    try:
        person = await PersonService.create_person(db, person_data, current_user.id)
        await db.commit()
        return person
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{person_id}", response_model=PersonResponse)
async def update_person(
    person_id: int,
    person_update: PersonUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """更新成员信息"""
    person = await PersonService.get_person_by_id(db, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="成员不存在")
    
    is_superuser = await FamilyService.is_superuser(db, current_user.id)
    if is_superuser:
        try:
            updated_person = await PersonService.update_person(db, person, person_update)
            await db.commit()
            return updated_person
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    can_manage = await FamilyService.can_manage_family_members(db, person.family_id, current_user.id)
    role = await FamilyService.get_user_role_in_family(db, person.family_id, current_user.id)
    
    if person.created_by != current_user.id and not can_manage and role not in ["admin", "family_admin", "editor"]:
        raise HTTPException(status_code=403, detail="您没有权限编辑此成员")
    
    try:
        updated_person = await PersonService.update_person(db, person, person_update)
        await db.commit()
        return updated_person
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_person(
    person_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """删除成员"""
    person = await PersonService.get_person_by_id(db, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="成员不存在")
    
    is_superuser = await FamilyService.is_superuser(db, current_user.id)
    can_delete = await FamilyService.can_delete_family_members(db, person.family_id, current_user.id)
    
    if not is_superuser and person.created_by != current_user.id and not can_delete:
        raise HTTPException(status_code=403, detail="您没有权限删除此成员")
    
    # 删除照片
    if person.photo_url:
        delete_file(person.photo_url)
    
    await PersonService.delete_person(db, person)
    await db.commit()
    return None

@router.post("/{person_id}/photo")
async def upload_person_photo(
    person_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """上传成员照片"""
    import traceback
    print(f"收到上传请求: person_id={person_id}, filename={file.filename}, content_type={file.content_type}")
    
    try:
        person = await PersonService.get_person_by_id(db, person_id)
        if not person:
            raise HTTPException(status_code=404, detail="成员不存在")
        
        is_superuser = await FamilyService.is_superuser(db, current_user.id)
        can_manage = await FamilyService.can_manage_family_members(db, person.family_id, current_user.id)
        role = await FamilyService.get_user_role_in_family(db, person.family_id, current_user.id)
        
        if not is_superuser and person.created_by != current_user.id and not can_manage and role not in ["editor"]:
            raise HTTPException(status_code=403, detail="您没有权限编辑此成员")
        
        print(f"权限检查通过，开始保存文件")
        file_path = save_upload_file(file, subfolder="photos")
        print(f"文件保存成功: {file_path}")
        
        # 删除旧照片
        if person.photo_url:
            delete_file(person.photo_url)
        
        # 更新照片URL
        print(f"开始更新数据库，person_id={person_id}, photo_url={file_path}")
        updated_person = await PersonService.update_person(
            db, person, {"photo_url": file_path}
        )
        print(f"update_person 返回: {updated_person}")
        print(f"person.photo_url 更新后: {person.photo_url}")
        
        await db.commit()
        print(f"数据库 commit 成功")
        
        # 重新查询验证
        verify_person = await PersonService.get_person_by_id(db, person_id)
        print(f"验证查询 - photo_url: {verify_person.photo_url if verify_person else 'None'}")
        
        return {"photo_url": file_path}
    except HTTPException:
        raise
    except Exception as e:
        error_detail = f"上传失败: {str(e)}\n{traceback.format_exc()}"
        print(error_detail)
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")

@router.get("/{person_id}/tree", response_model=dict)
async def get_person_tree(
    person_id: int,
    max_generations: int = Query(10, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
    current_user: Optional = Depends(get_current_active_user)
):
    """获取成员家谱树"""
    person = await PersonService.get_person_by_id(db, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="成员不存在")
    
    # 检查访问权限
    family = await FamilyService.get_family_by_id(db, person.family_id)
    if not family.is_public:
        if not current_user:
            raise HTTPException(status_code=403, detail="该家族为私密家族")
        role = await FamilyService.get_user_role_in_family(db, person.family_id, current_user.id)
        if not role:
            raise HTTPException(status_code=403, detail="您没有权限访问此家族")
    
    tree_data = await PersonService.build_family_tree(db, person_id, max_generations)
    if not tree_data:
        raise HTTPException(status_code=404, detail="无法构建家谱树")
    
    return tree_data

@router.post("/relationships", response_model=RelationshipResponse, status_code=status.HTTP_201_CREATED)
async def create_relationship(
    rel_data: RelationshipCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """创建亲属关系"""
    # 检查两个成员是否属于同一家族
    person = await PersonService.get_person_by_id(db, rel_data.person_id)
    relative = await PersonService.get_person_by_id(db, rel_data.relative_id)
    
    if not person or not relative:
        raise HTTPException(status_code=404, detail="成员不存在")
    
    if person.family_id != relative.family_id:
        raise HTTPException(status_code=400, detail="两个成员必须属于同一家族")
    
    # 检查权限
    role = await FamilyService.get_user_role_in_family(db, person.family_id, current_user.id)
    if not role:
        raise HTTPException(status_code=403, detail="您没有权限在此家族添加关系")
    
    try:
        rel = await PersonService.create_relationship(db, rel_data)
        await db.commit()
        return rel
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{person_id}/relationships", response_model=List[RelationshipResponse])
async def get_person_relationships(
    person_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Optional = Depends(get_current_active_user)
):
    """获取成员的所有亲属关系"""
    person = await PersonService.get_person_by_id(db, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="成员不存在")
    
    family = await FamilyService.get_family_by_id(db, person.family_id)
    if not family.is_public:
        if not current_user:
            raise HTTPException(status_code=403, detail="该家族为私密家族")
        role = await FamilyService.get_user_role_in_family(db, person.family_id, current_user.id)
        if not role:
            raise HTTPException(status_code=403, detail="您没有权限访问此家族")
    
    relationships = await PersonService.get_relationships(db, person_id)
    
    result = []
    for rel in relationships:
        relative = await PersonService.get_person_by_id(db, rel.relative_id)
        result.append(RelationshipResponse(
            id=rel.id,
            person_id=rel.person_id,
            relative_id=rel.relative_id,
            relation_type=rel.relation_type,
            is_primary=rel.is_primary,
            marriage_date=rel.marriage_date,
            divorce_date=rel.divorce_date,
            created_at=rel.created_at,
            person_name=person.name,
            relative_name=relative.name if relative else None
        ))
    
    return result

@router.put("/relationships/{relationship_id}", response_model=RelationshipResponse)
async def update_relationship(
    relationship_id: int,
    rel_update: RelationshipUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """更新亲属关系"""
    relationship = await PersonService.get_relationship_by_id(db, relationship_id)
    if not relationship:
        raise HTTPException(status_code=404, detail="关系不存在")
    
    person = await PersonService.get_person_by_id(db, relationship.person_id)
    if not person:
        raise HTTPException(status_code=404, detail="成员不存在")
    
    role = await FamilyService.get_user_role_in_family(db, person.family_id, current_user.id)
    if not role:
        raise HTTPException(status_code=403, detail="您没有权限编辑此关系")
    
    try:
        updated_rel = await PersonService.update_relationship(db, relationship, rel_update)
        await db.commit()
        
        relative = await PersonService.get_person_by_id(db, updated_rel.relative_id)
        return RelationshipResponse(
            id=updated_rel.id,
            person_id=updated_rel.person_id,
            relative_id=updated_rel.relative_id,
            relation_type=updated_rel.relation_type,
            is_primary=updated_rel.is_primary,
            marriage_date=updated_rel.marriage_date,
            divorce_date=updated_rel.divorce_date,
            created_at=updated_rel.created_at,
            person_name=person.name,
            relative_name=relative.name if relative else None
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/relationships/{relationship_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_relationship(
    relationship_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """删除亲属关系"""
    relationship = await PersonService.get_relationship_by_id(db, relationship_id)
    if not relationship:
        raise HTTPException(status_code=404, detail="关系不存在")
    
    person = await PersonService.get_person_by_id(db, relationship.person_id)
    if not person:
        raise HTTPException(status_code=404, detail="成员不存在")
    
    role = await FamilyService.get_user_role_in_family(db, person.family_id, current_user.id)
    if not role:
        raise HTTPException(status_code=403, detail="您没有权限删除此关系")
    
    await PersonService.delete_relationship(db, relationship)
    await db.commit()
    return None
