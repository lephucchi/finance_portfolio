import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import {
  BarChart3,
  TrendingUp,
  FileText,
  BarChart2,
  Zap,
  MessageSquare,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface SidebarProps {
  isCollapsed?: boolean;
  onToggleCollapse?: () => void;
}

const MENU_ITEMS = [
  { id: "dashboard", label: "Dashboard", icon: BarChart3, path: "/" },
  { id: "screener", label: "Asset Finder", icon: BarChart2, path: "/screener" },
  { id: "news", label: "Insights", icon: FileText, path: "/news" },
  { id: "trends", label: "Forecasts", icon: TrendingUp, path: "/trends" },
  { id: "reports", label: "Reports", icon: Zap, path: "/reports" },
  { id: "chat", label: "Oracle", icon: MessageSquare, path: "/chat" },
];

export default function Sidebar({
  isCollapsed = false,
  onToggleCollapse,
}: SidebarProps) {
  const navigate = useNavigate();
  const location = useLocation();
  const [collapsed, setCollapsed] = useState(isCollapsed);

  const handleCollapse = () => {
    setCollapsed(!collapsed);
    onToggleCollapse?.();
  };

  const isActive = (path: string) => {
    if (path === "/" && location.pathname === "/") return true;
    if (path !== "/" && location.pathname.startsWith(path)) return true;
    return false;
  };

  return (
    <aside
      className={cn(
        "fixed left-0 top-16 bottom-0 border-r border-border/30 bg-sidebar glass-panel transition-all duration-300 z-40 rounded-none",
        collapsed ? "w-20" : "w-64",
      )}
    >
      <div className="flex flex-col h-full">
        {/* Menu Items */}
        <nav className="flex-1 px-3 py-4 space-y-1">
          {MENU_ITEMS.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.path);

            return (
              <button
                key={item.id}
                onClick={() => navigate(item.path)}
                className={cn(
                  "w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-300",
                  active
                    ? "bg-primary/10 text-primary shadow-md"
                    : "text-sidebar-foreground hover:bg-secondary/50",
                )}
              >
                <Icon className="w-5 h-5 flex-shrink-0" />
                {!collapsed && (
                  <span className="text-sm font-medium">{item.label}</span>
                )}
              </button>
            );
          })}
        </nav>

        {/* Footer Section */}
        <div className="p-3 border-t border-border/30 space-y-3">
          {/* Collapse Toggle */}
          <button
            onClick={handleCollapse}
            className="w-full flex items-center justify-center py-2.5 rounded-lg border border-border/30 hover:bg-secondary/50 hover:shadow-md transition-all duration-300"
          >
            {collapsed ? (
              <ChevronRight className="w-4 h-4" />
            ) : (
              <ChevronLeft className="w-4 h-4" />
            )}
          </button>
        </div>
      </div>
    </aside>
  );
}
