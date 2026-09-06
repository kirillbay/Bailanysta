import { NavLink, Outlet, useLocation } from "react-router-dom";
import { useTranslation } from "react-i18next";
import {
  Home,
  Search,
  UsersRound,
  FolderKanban,
  MessageCircle,
  Bell,
  User,
  Settings,
  Globe,
  Sun,
  Moon,
  Monitor,
} from "lucide-react";
import { useTheme } from "@/stores/theme";
import { useAuth } from "@/stores/auth";
import { cn } from "@/lib/utils";
import { useQuery } from "@tanstack/react-query";
import { notificationsApi } from "@/api/notifications";
import { useNotificationsRealtime } from "@/hooks/useRealtime";

const navItems = [
  { to: "/", icon: Home, key: "nav.feed" },
  { to: "/search", icon: Search, key: "nav.search" },
  { to: "/clubs", icon: UsersRound, key: "nav.clubs" },
  { to: "/projects", icon: FolderKanban, key: "nav.projects" },
  { to: "/messages", icon: MessageCircle, key: "nav.messages" },
  { to: "/notifications", icon: Bell, key: "nav.notifications" },
  { to: "/profile", icon: User, key: "nav.profile" },
  { to: "/settings", icon: Settings, key: "nav.settings" },
] as const;

function LanguageSwitcher() {
  const { i18n } = useTranslation();
  const langs = [
    { code: "ru", label: "RU" },
    { code: "kk", label: "KZ" },
    { code: "en", label: "EN" },
  ] as const;
  return (
    <div className="flex items-center gap-1 rounded-full border bg-card p-1">
      <Globe className="ml-1 h-3.5 w-3.5 text-muted-foreground" />
      {langs.map((l) => (
        <button
          key={l.code}
          onClick={() => i18n.changeLanguage(l.code)}
          className={cn(
            "rounded-full px-2.5 py-1 text-xs font-medium transition-colors",
            i18n.language?.startsWith(l.code) ? "bg-foreground text-background" : "hover:bg-accent",
          )}
        >
          {l.label}
        </button>
      ))}
    </div>
  );
}

function ThemeSwitcher() {
  const { theme, setTheme } = useTheme();
  const opts: Array<{ v: "light" | "dark" | "system"; icon: typeof Sun }> = [
    { v: "light", icon: Sun },
    { v: "dark", icon: Moon },
    { v: "system", icon: Monitor },
  ];
  return (
    <div className="flex items-center gap-1 rounded-full border bg-card p-1">
      {opts.map((o) => {
        const Icon = o.icon;
        return (
          <button
            key={o.v}
            onClick={() => setTheme(o.v)}
            className={cn(
              "rounded-full p-1.5 transition-colors",
              theme === o.v ? "bg-foreground text-background" : "hover:bg-accent",
            )}
            aria-label={o.v}
          >
            <Icon className="h-3.5 w-3.5" />
          </button>
        );
      })}
    </div>
  );
}

function Sidebar() {
  const { t } = useTranslation();
  const { user, logout, isAuthenticated } = useAuth();
  const notifQuery = useQuery({ queryKey: ["notifications-unread"], queryFn: () => notificationsApi.unreadCount(), enabled: isAuthenticated });
  useNotificationsRealtime();
  return (
    <aside className="hidden w-[260px] shrink-0 flex-col gap-4 border-r bg-card/50 p-4 lg:flex">
      <div className="flex items-center gap-2.5 px-2 py-2">
        <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-foreground text-background font-bold text-sm">
          Б
        </div>
        <div>
          <div className="text-sm font-semibold leading-none">Bailanysta</div>
          <div className="text-[11px] text-muted-foreground">IT community</div>
        </div>
      </div>

      <nav className="flex flex-col gap-1">
        {navItems.map((item) => {
          const count = item.to === "/notifications" ? notifQuery.data?.count : undefined;
          const displayCount = count && count > 99 ? "99+" : count;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium transition-colors",
                  isActive ? "bg-foreground text-background" : "hover:bg-accent text-muted-foreground hover:text-foreground",
                )
              }
            >
              <item.icon className="h-4 w-4" />
              {t(item.key, item.key)}
              {count ? <span className="ml-auto rounded-full bg-red-500 px-1.5 py-0.5 text-[10px] text-white">{displayCount}</span> : null}
            </NavLink>
          );
        })}
      </nav>

      <div className="mt-auto flex flex-col gap-3 pt-4">
        {isAuthenticated && user && (
          <div className="rounded-xl border bg-background p-3">
            <p className="text-xs font-medium truncate">@{user.username}</p>
            <p className="text-xs text-muted-foreground truncate">{user.email}</p>
            <button onClick={logout} className="mt-2 text-xs font-medium text-foreground underline">
              Выйти
            </button>
          </div>
        )}
        <LanguageSwitcher />
        <ThemeSwitcher />
        <div className="rounded-xl border bg-background p-3">
          <p className="text-xs font-medium">Байланыста болайық</p>
          <p className="text-xs text-muted-foreground">Будь на связи с IT-комьюнити</p>
        </div>
      </div>
    </aside>
  );
}

function BottomNav() {
  const location = useLocation();
  // show only primary nav on mobile
  const mobileNav = navItems.slice(0, 5);
  return (
    <nav className="fixed bottom-0 left-0 right-0 z-40 flex items-center justify-around border-t bg-background/95 px-2 py-2 backdrop-blur lg:hidden">
      {mobileNav.map((item) => {
        const active = location.pathname === item.to;
        return (
          <NavLink
            key={item.to}
            to={item.to}
            className={cn(
              "flex flex-col items-center gap-1 rounded-xl px-3 py-1.5 text-[11px] font-medium",
              active ? "text-foreground" : "text-muted-foreground",
            )}
          >
            <item.icon className={cn("h-5 w-5", active && "fill-foreground/10")} />
          </NavLink>
        );
      })}
    </nav>
  );
}

function TopBar() {
  const { t } = useTranslation();
  return (
    <header className="sticky top-0 z-30 flex h-14 items-center justify-between border-b bg-background/80 px-4 backdrop-blur lg:hidden">
      <div className="flex items-center gap-2">
        <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-foreground text-background font-bold text-xs">
          Б
        </div>
        <span className="text-sm font-semibold">Bailanysta</span>
      </div>
      <div className="flex items-center gap-2">
        <span className="text-xs text-muted-foreground hidden sm:inline">{t("common.tagline")}</span>
      </div>
    </header>
  );
}

export function AppShell() {
  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <div className="flex flex-1 flex-col">
        <TopBar />
        <main className="flex-1 pb-16 lg:pb-0">
          <div className="mx-auto w-full max-w-[1080px] p-4 sm:p-6">
            <Outlet />
          </div>
        </main>
        <BottomNav />
      </div>
    </div>
  );
}
