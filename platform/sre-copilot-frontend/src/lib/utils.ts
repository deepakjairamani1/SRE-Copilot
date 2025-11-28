import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(date: string | Date) {
  return new Date(date).toLocaleString()
}

export function formatDuration(seconds: number) {
  return `${seconds.toFixed(2)}s`
}

export function formatCost(cost: number) {
  return `$${cost.toFixed(4)}`
}