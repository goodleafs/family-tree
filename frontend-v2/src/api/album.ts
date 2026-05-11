import request from './request'
import type { Album, AlbumDetail, Photo, AlbumTimeline, ListResponse } from '@/types'

export const albumApi = {
  getAlbums: (familyId: number, params?: { skip?: number; limit?: number }): Promise<ListResponse<Album>> => {
    return request.get(`/albums/family/${familyId}`, { params })
  },

  getAlbum: (albumId: number): Promise<AlbumDetail> => {
    return request.get(`/albums/${albumId}`)
  },

  createAlbum: (data: { family_id: number; name: string; description?: string }): Promise<Album> => {
    return request.post('/albums', data)
  },

  updateAlbum: (albumId: number, data: Partial<Album>): Promise<Album> => {
    return request.put(`/albums/${albumId}`, data)
  },

  deleteAlbum: (albumId: number): Promise<void> => {
    return request.delete(`/albums/${albumId}`)
  },

  getAlbumPhotos: (albumId: number, params?: { skip?: number; limit?: number }): Promise<ListResponse<Photo>> => {
    return request.get(`/albums/${albumId}/photos`, { params })
  },

  uploadPhoto: (albumId: number, file: File, data?: { title?: string; description?: string; taken_date?: string }): Promise<Photo> => {
    const formData = new FormData()
    formData.append('file', file)
    return request.post(`/albums/${albumId}/photos`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      params: data
    })
  },

  updatePhoto: (photoId: number, data: Partial<Photo>): Promise<Photo> => {
    return request.put(`/albums/photos/${photoId}`, data)
  },

  deletePhoto: (photoId: number): Promise<void> => {
    return request.delete(`/albums/photos/${photoId}`)
  },

  getTimeline: (familyId: number): Promise<AlbumTimeline> => {
    return request.get(`/albums/family/${familyId}/timeline`)
  }
}
