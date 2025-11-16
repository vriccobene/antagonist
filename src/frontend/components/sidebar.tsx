"use client"

import { useState } from "react"
import { usePathname } from "next/navigation"
import { ChevronLeft, LayoutDashboard, Database, TrendingUp, AlertTriangle, Network } from "lucide-react"
import { cn } from "@/lib/utils"
import Link from "next/link"
import { ThemeToggle } from "@/components/theme-toggle"

interface SidebarProps {
  className?: string
}

const menuItems = [
  {
    title: "Dashboard",
    icon: LayoutDashboard,
    href: "/dashboard",
    section: null,
  },
  // {
  //   title: "Detection Models",
  //   icon: Shield,
  //   href: "/detection-models",
  //   section: "Detection",
  // },
  {
    title: "Incidents",
    icon: AlertTriangle,
    href: "/incidents",
    section: "Refinement",
  },
  {
    title: "Anomalies",
    icon: TrendingUp,
    href: "/anomalies",
    section: "Validation",
  },
  // {
  //   title: "Symptoms",
  //   icon: AlertCircle,
  //   href: "/symptoms",
  //   section: "Validation",
  // },
  {
    title: "Data Sources",
    icon: Database,
    href: "/data-sources",
    section: "Configuration",
  },
  // {
  //   title: "Monitored Entities",
  //   icon: Network, // Changed from Database to Network icon
  //   href: "/monitored-entities",
  //   section: "Configuration",
  // },
  {
    title: "Monitored Entity Types",
    icon: Network, // Changed from Database to Network icon
    href: "/monitored-entity-types",
    section: "Configuration",
  },
  // {
  //   title: "Refinement",
  //   icon: RotateCcw,
  //   href: "/refinement",
  //   section: "Refinement",
  // },
  // {
  //   title: "Datasets",
  //   icon: FileText,
  //   href: "/datasets",
  //   section: "Refinement",
  // },
]

const sections = ["Detection", "Validation", "Refinement"]

export function Sidebar({ className }: SidebarProps) {
  const [isCollapsed, setIsCollapsed] = useState(false)
  const pathname = usePathname()

  return (
    <div
      className={cn(
        "flex h-screen flex-col border-r bg-sidebar text-sidebar-foreground transition-all duration-300",
        isCollapsed ? "w-16" : "w-64",
        className,
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-sidebar-border">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-600">
            <span className="text-sm font-bold text-white">A</span>
          </div>
          {!isCollapsed && <span className="text-lg font-semibold">Antagonist</span>}
        </div>
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="rounded-md p-1 hover:bg-sidebar-accent transition-colors"
        >
          <ChevronLeft className={cn("h-4 w-4 transition-transform duration-300", isCollapsed && "rotate-180")} />
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto p-2">
        <div className="space-y-1">
          {menuItems.map((item, index) => {
            const showSectionHeader = item.section && (index === 0 || menuItems[index - 1].section !== item.section)
            const isActive = pathname === item.href

            return (
              <div key={item.href}>
                {showSectionHeader && (
                  <div
                    className={cn(
                      "px-3 py-2 text-xs font-medium text-muted-foreground uppercase tracking-wider",
                      isCollapsed && "hidden",
                    )}
                  >
                    {item.section}
                  </div>
                )}
                <Link
                  href={item.href}
                  className={cn(
                    "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors hover:bg-sidebar-accent",
                    isActive && "bg-blue-600/20 text-blue-400",
                    isCollapsed && "justify-center px-2",
                  )}
                >
                  <item.icon className="h-5 w-5 flex-shrink-0" />
                  {!isCollapsed && <span className="truncate">{item.title}</span>}
                </Link>
              </div>
            )
          })}
        </div>
      </nav>

      {/* Theme Toggle */}
      <div className="p-4 border-t border-sidebar-border">
        <div className={cn("flex items-center", isCollapsed ? "justify-center" : "justify-between")}>
          {!isCollapsed && <span className="text-sm text-muted-foreground">Theme</span>}
          <ThemeToggle />
        </div>
      </div>
    </div>
  )
}
