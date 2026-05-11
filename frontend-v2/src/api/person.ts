import request from './request'
import type { Person, Relationship, FamilyTree, ListResponse } from '@/types'

export interface PersonCreate {
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
}

export interface PersonUpdate {
  name?: string
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
}

export const personApi = {
  getPersons: (params?: { family_id?: number; search?: string; skip?: number; limit?: number }): Promise<ListResponse<Person>> => {
    return request.get('/persons', { params })
  },

  getFamilyPersons: (familyId: number): Promise<ListResponse<Person>> => {
    return request.get(`/persons/family/${familyId}`)
  },

  getPerson: (id: number): Promise<Person> => {
    return request.get(`/persons/${id}`)
  },

  createPerson: (data: PersonCreate): Promise<Person> => {
    return request.post('/persons', data)
  },

  updatePerson: (id: number, data: PersonUpdate): Promise<Person> => {
    return request.put(`/persons/${id}`, data)
  },

  deletePerson: (id: number): Promise<void> => {
    return request.delete(`/persons/${id}`)
  },

  getRelationships: (personId: number): Promise<Relationship[]> => {
    return request.get(`/persons/${personId}/relationships`)
  },

  addRelationship: (personId: number, data: { relative_id: number; relation_type: string; is_primary?: boolean }): Promise<Relationship> => {
    return request.post(`/persons/${personId}/relationships`, data)
  },

  deleteRelationship: (personId: number, relationshipId: number): Promise<void> => {
    return request.delete(`/persons/${personId}/relationships/${relationshipId}`)
  },

  getFamilyTree: (personId: number): Promise<FamilyTree> => {
    return request.get(`/persons/${personId}/tree`)
  },

  uploadPhoto: (personId: number, file: File): Promise<{ photo_url: string }> => {
    const formData = new FormData()
    formData.append('file', file)
    return request.post(`/persons/${personId}/photo`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  }
}