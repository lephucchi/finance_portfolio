import { useState } from "react";
import { Search, Sun, Moon, LogOut } from "lucide-react";
import { cn } from "@/lib/utils";
import LanguageSwitcher from "./LanguageSwitcher";

interface HeaderProps {
  isDarkMode: boolean;
  onToggleDarkMode: () => void;
}

export default function Header({ isDarkMode, onToggleDarkMode }: HeaderProps) {
  const [searchFocus, setSearchFocus] = useState(false);

  return (
    <header className="fixed top-0 left-0 right-0 z-40 glass-panel border-b border-border/30">
      <div className="flex h-16 items-center justify-between px-6">
        {/* Logo & Branding */}
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-lg flex items-center justify-center">
            <img 
              src="/AEGIS_LUMINA.png" 
              alt="AEGIS LUMINA Logo" 
              className="w-12 h-12 object-contain"
            />
          </div>
          <div className="flex flex-col">
            <span className="font-semibold text-base tracking-tight hidden sm:inline text-foreground">
              AEGIS LUMINA
            </span>
            <span className="text-xs text-muted-foreground hidden sm:inline">
              The AI Shield
            </span>
          </div>
        </div>

        {/* Search Bar */}
        <div className="flex-1 max-w-md mx-4">
          <div
            className={cn(
              "flex items-center gap-2 px-4 py-2 rounded-lg border transition-all duration-300",
              "bg-secondary/30 border-border/40",
              searchFocus && "border-primary/50 bg-background/60 shadow-md",
            )}
          >
            <Search className="w-4 h-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search insights, assets..."
              className="flex-1 bg-transparent outline-none text-sm placeholder-muted-foreground text-foreground"
              onFocus={() => setSearchFocus(true)}
              onBlur={() => setSearchFocus(false)}
            />
          </div>
        </div>

        {/* Right Actions */}
        <div className="flex items-center gap-2 sm:gap-4">
          {/* Language Switcher */}
          <LanguageSwitcher />

          {/* Theme Toggle with Smooth Animation */}
          <button
            onClick={onToggleDarkMode}
            className={cn(
              "p-2.5 rounded-lg transition-all duration-300",
              "hover:bg-secondary/50 hover:shadow-md",
              "border border-border/30",
            )}
            title={isDarkMode ? "Switch to Daybreak" : "Switch to Starlight"}
          >
            {isDarkMode ? (
              <Sun className="w-4 h-4 text-primary animate-soft-glow" />
            ) : (
              <Moon className="w-4 h-4 text-primary" />
            )}
          </button>

          {/* Logout */}
          <button className="p-2.5 rounded-lg hover:bg-secondary/50 hover:shadow-md border border-border/30 transition-all duration-300 hidden sm:flex">
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </header>
  );
}
