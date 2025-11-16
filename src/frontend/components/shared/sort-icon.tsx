import { ArrowUp, ArrowDown, ArrowUpDown } from "lucide-react"

interface SortIconProps {
  column: string
  sortConfig: { key: string; direction: "asc" | "desc" } | null
}

export function SortIcon({ column, sortConfig }: SortIconProps) {
  if (!sortConfig || sortConfig.key !== column) {
    return <ArrowUpDown className="w-4 h-4 ml-1 text-gray-500" />
  }
  return sortConfig.direction === "asc" ? (
    <ArrowUp className="w-4 h-4 ml-1 text-blue-400" />
  ) : (
    <ArrowDown className="w-4 h-4 ml-1 text-blue-400" />
  )
}
