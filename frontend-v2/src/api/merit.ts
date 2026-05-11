import request from './request'
import type { MeritDonor, MeritDonorListResponse } from '@/types'

export const meritApi = {
  getDonors: (familyId: number, params?: { skip?: number; limit?: number }): Promise<MeritDonorListResponse> => {
    return request.get(`/merit/family/${familyId}`, { params })
  },

  getDonor: (donorId: number): Promise<MeritDonor> => {
    return request.get(`/merit/${donorId}`)
  },

  createDonor: (data: { family_id: number; donor_name: string; amount: number; donation_date?: string; remarks?: string; sort_order?: number }): Promise<MeritDonor> => {
    return request.post('/merit', data)
  },

  updateDonor: (donorId: number, data: Partial<MeritDonor>): Promise<MeritDonor> => {
    return request.put(`/merit/${donorId}`, data)
  },

  deleteDonor: (donorId: number): Promise<void> => {
    return request.delete(`/merit/${donorId}`)
  }
}
