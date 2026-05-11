// 类型定义文件

// 用户相关
export interface User {
  id: number
  username: string
  email?: string
  phone?: string
  avatar_url?: string
  is_active: boolean
  is_superuser?: boolean
  created_at: string
}

export interface UserLogin {
  username: string
  password: string
}

export interface UserRegister {
  username: string
  password: string
  email?: string
  phone?: string
}

export interface Token {
  access_token: string
  token_type: string
}

// 家族相关
export interface Family {
  id: number
  name: string
  surname?: string
  description?: string
  history?: string
  family_motto?: string
  generation_names?: string[]
  creator_id: number
  is_public: boolean
  created_at: string
  updated_at: string
  member_count?: number
  person_count?: number
}

export interface FamilyMember {
  id: number
  family_id: number
  user_id: number
  role: 'admin' | 'family_admin' | 'editor' | 'member'
  username?: string
  created_at: string
}

export interface FamilyMemberInfo {
  id: number
  family_id: number
  user_id: number
  role: 'admin' | 'family_admin' | 'editor' | 'member'
  username: string
  email?: string
  avatar_url?: string
  is_superuser?: boolean
  created_at: string
}

// 成员相关
export interface Person {
  id: number
  family_id: number
  name: string
  gender?: 'male' | 'female'
  birth_date?: string
  death_date?: string
  birthplace?: string
  residence?: string
  occupation?: string
  education?: string
  biography?: string
  achievements?: string
  photo_url?: string
  branch_name?: string
  generation_number?: number
  created_by?: number
  created_at: string
  updated_at: string
}

export interface Relationship {
  id: number
  person_id: number
  relative_id: number
  relation_type: 'father' | 'mother' | 'spouse' | 'child'
  is_primary: boolean
  marriage_date?: string
  divorce_date?: string
  person_name?: string
  relative_name?: string
  created_at: string
}

export interface RelationshipCreate {
  person_id: number
  relative_id: number
  relation_type: 'father' | 'mother' | 'spouse' | 'child'
  is_primary?: boolean
  marriage_date?: string
  divorce_date?: string
}

export interface RelationshipUpdate {
  is_primary?: boolean
  marriage_date?: string
  divorce_date?: string
}

// 族谱树节点
export interface TreeNode {
  id: number
  name: string
  gender?: string
  birth_date?: string
  death_date?: string
  photo_url?: string
  generation_number?: number
  children: TreeNode[]
  spouses: TreeNode[]
}

export interface FamilyTree {
  root: TreeNode
  total_generations: number
  total_members: number
}

// 相册相关
export interface Album {
  id: number
  family_id: number
  name: string
  description?: string
  cover_url?: string
  sort_order: number
  created_by: number
  created_at: string
  updated_at: string
  photo_count?: number
}

export interface AlbumDetail extends Album {
  photos: Photo[]
}

export interface Photo {
  id: number
  album_id?: number
  family_id: number
  title?: string
  description?: string
  url: string
  thumbnail_url?: string
  taken_date?: string
  taken_year?: number
  taken_month?: number
  file_size?: number
  uploader_id: number
  created_at: string
}

export interface TimelineGroup {
  year: number
  photos: Photo[]
}

export interface AlbumTimeline {
  total: number
  years: number[]
  timeline: TimelineGroup[]
}

// 文献相关
export interface Document {
  id: number
  family_id: number
  title: string
  description?: string
  file_type: string
  file_url: string
  file_size?: number
  file_ext?: string
  author?: string
  document_date?: string
  tags?: string
  category?: string
  uploader_id: number
  created_at: string
  updated_at: string
}

export interface DocumentCategoryCount {
  category: string
  count: number
}

export interface DocumentOverview {
  total: number
  pdf_count: number
  image_count: number
  categories: DocumentCategoryCount[]
}

// 传记相关
export interface PersonBrief {
  id: number
  name: string
  gender?: string
  birth_date?: string
  death_date?: string
  photo_url?: string
  branch_name?: string
  generation_number?: number
}

export interface Biography {
  id: number
  title?: string
  subtitle?: string
  summary?: string
  content: string
  achievements?: string
  portrait_url?: string
  is_published: boolean
  views_count: number
  person: PersonBrief
  created_by: number
  created_at: string
  updated_at: string
}

export interface BiographyListItem {
  id: number
  title?: string
  person: PersonBrief
  summary?: string
  views_count: number
  is_published: boolean
  created_by: number
  created_at: string
  updated_at: string
}

// API 响应
export interface ApiResponse<T> {
  data: T
  message?: string
}

export interface ListResponse<T> {
  total: number
  items: T[]
}
