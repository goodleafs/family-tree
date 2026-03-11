import { Lunar } from 'lunar-javascript'

/**
 * 将公历日期转换为农历日期字符串
 * @param dateString 公历日期字符串 (YYYY-MM-DD)
 * @returns 农历日期字符串，如"二零二四年正月初一"
 */
export function toLunarDate(dateString?: string): string {
  if (!dateString) return '-'

  try {
    const date = new Date(dateString)
    const lunar = Lunar.fromDate(date)
    return lunar.toString()
  } catch (error) {
    console.error('农历转换失败:', error)
    return '-'
  }
}

/**
 * 将公历日期转换为农历日期（简化格式）
 * @param dateString 公历日期字符串 (YYYY-MM-DD)
 * @returns 农历日期字符串，如"正月初一"
 */
export function toLunarDateShort(dateString?: string): string {
  if (!dateString) return '-'

  try {
    const date = new Date(dateString)
    const lunar = Lunar.fromDate(date)
    return lunar.getMonthInChinese() + '月' + lunar.getDayInChinese()
  } catch (error) {
    console.error('农历转换失败:', error)
    return '-'
  }
}

/**
 * 获取农历年份（干支纪年）
 * @param dateString 公历日期字符串 (YYYY-MM-DD)
 * @returns 农历年份，如"甲辰年"
 */
export function toLunarYear(dateString?: string): string {
  if (!dateString) return '-'

  try {
    const date = new Date(dateString)
    const lunar = Lunar.fromDate(date)
    return lunar.getYearInGanZhi() + '年'
  } catch (error) {
    console.error('农历转换失败:', error)
    return '-'
  }
}

/**
 * 获取农历年份+日期（干支纪年+月日）
 * @param dateString 公历日期字符串 (YYYY-MM-DD)
 * @returns 农历日期字符串，如"甲辰年正月初一"
 */
export function toLunarYearWithDate(dateString?: string): string {
  if (!dateString) return '-'

  try {
    const date = new Date(dateString)
    const lunar = Lunar.fromDate(date)
    return lunar.getYearInGanZhi() + '年' + lunar.getMonthInChinese() + '月' + lunar.getDayInChinese()
  } catch (error) {
    console.error('农历转换失败:', error)
    return '-'
  }
}

