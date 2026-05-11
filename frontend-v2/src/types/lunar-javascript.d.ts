declare module 'lunar-javascript' {
  export class Solar {
    static fromDate(date: Date): Solar
    getLunar(): Lunar
    getYear(): number
    getMonth(): number
    getDay(): number
  }

  export class Lunar {
    static fromDate(date: Date): Lunar
    getYearInChinese(): string
    getYearInGanZhi(): string
    getMonthInChinese(): string
    getDayInChinese(): string
    getYearShengXiao(): string
    toString(): string
    getYear(): number
    getMonth(): number
    getDay(): number
  }
}