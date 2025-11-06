import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import {
  Home,
  BarChart3,
  TrendingUp,
  FileText,
  BarChart2,
  Zap,
  MessageSquare,
  ChevronLeft,
  ChevronRight,
  Info,
  Book,
  AlertTriangle,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface SidebarProps {
  isCollapsed?: boolean;
  onToggleCollapse?: () => void;
}

const MENU_ITEMS = [
  { id: "home", label: "Home", icon: Home, path: "/", badge: null },
  { id: "chat", label: "Metallica", icon: MessageSquare, path: "/chat", badge: null },
  { id: "dashboard", label: "Dashboard", icon: BarChart3, path: "/dashboard", badge: null },
  { id: "screener", label: "Asset Finder", icon: BarChart2, path: "/screener", badge: null },
  { id: "news", label: "Insights", icon: FileText, path: "/news", badge: "DEMO" },
  { id: "trends", label: "Forecasts", icon: TrendingUp, path: "/trends", badge: "DEMO" },
  { id: "reports", label: "Reports", icon: Zap, path: "/reports", badge: "DEMO" },
];

const INFO_ITEMS = [
  { id: "about", label: "About", icon: Info, path: "/about" },
  { id: "guide", label: "Guide", icon: Book, path: "/guide" },
  { id: "disclaimer", label: "Disclaimer", icon: AlertTriangle, path: "/disclaimer" },
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
                  <div className="flex items-center justify-between flex-1">
                    <span className="text-sm font-medium">{item.label}</span>
                    {item.badge && (
                      <span className="px-2 py-0.5 text-[10px] font-bold bg-yellow-100 text-yellow-800 rounded border border-yellow-300">
                        {item.badge}
                      </span>
                    )}
                  </div>
                )}
              </button>
            );
          })}

          {/* Information Section */}
          {!collapsed && (
            <div className="pt-4 mt-4 border-t border-border/30">
              <p className="px-3 pb-2 text-xs font-semibold text-muted-foreground uppercase tracking-wide">
                Information
              </p>
            </div>
          )}
          {INFO_ITEMS.map((item) => {
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
