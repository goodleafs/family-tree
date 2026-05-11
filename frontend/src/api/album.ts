import request from './request'
import type { Album, AlbumDetail, Photo, AlbumTimeline, ListResponse } from '@/types'

export const albumApi = {
  // 获取家族相册列表
  getAlbums: (familyId: number, params?: { skip?: number; limit?: number }): Promise<ListResponse<Album>> => {
    return request.get(`/albums/family/${familyId}`, { params })
  },

  // 获取相册详情
  getAlbum: (albumId: number): Promise<AlbumDetail> => {
    return request.get(`/albums/${albumId}`)
  },

  // 创建相册
  createAlbum: (data: { family_id: number; name: string; description?: string }): Promise<Album> => {
    return request.post('/albums', data)
  },

  // 更新相册
  updateAlbum: (albumId: number, data: Partial<Album>): Promise<Album> => {
    return request.put(`/albums/${albumId}`, data)
  },

  // 删除相册
  deleteAlbum: (albumId: number): Promise<void> => {
    return request.delete(`/albums/${albumId}`)
  },

  // 获取相册照片列表
  getAlbumPhotos: (albumId: number, params?: { skip?: number; limit?: number }): Promise<ListResponse<Photo>> => {
    return request.get(`/albums/${albumId}/photos`, { params })
  },

  // 上传照片到相册
  uploadPhoto: (albumId: number, file: File, data?: { title?: string; description?: string; taken_date?: string }): Promise<Photo> => {
    const formData = new FormData()
    formData.append('file', file)
    if (data?.title) formData.append('title', data.title)
    if (data?.description) formData.append('description', data.description)
    if (data?.taken_date) formData.append('taken_date', data.taken_date)
    return request.post(`/albums/${albumId}/photos`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      params: data
    })
  },

  // 更新照片信息
  updatePhoto: (photoId: number, data: Partial<Photo>): Promise<Photo> => {
    return request.put(`/albums/photos/${photoId}`, data)
  },

  // 删除照片
  deletePhoto: (photoId: number): Promise<void> => {
    return request.delete(`/albums/photos/${photoId}`)
  },

  // 获取家族照片时间轴
  getTimeline: (familyId: number): Promise<AlbumTimeline> => {
    return request.get(`/albums/family/${familyId}/timeline`)
  }
}
