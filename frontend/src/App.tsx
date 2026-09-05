import { createBrowserRouter, RouterProvider } from "react-router-dom";
import { AppShell } from "@/components/layout/AppShell";
import { FeedPage } from "@/pages/FeedPage";
import { PlaceholderPage } from "@/pages/PlaceholderPage";
import { NotFoundPage } from "@/pages/NotFoundPage";
import { LoginPage } from "@/pages/LoginPage";
import { RegisterPage } from "@/pages/RegisterPage";
import { RequireAuth } from "@/components/RequireAuth";

const router = createBrowserRouter([
  { path: "/login", element: <LoginPage /> },
  { path: "/register", element: <RegisterPage /> },
  {
    element: (
      <RequireAuth>
        <AppShell />
      </RequireAuth>
    ),
    errorElement: <NotFoundPage />,
    children: [
      { path: "/", element: <FeedPage /> },
      {
        path: "/explore",
        element: <PlaceholderPage titleKey="nav.explore" fallbackTitle="Explore" description="Рекомендации и популярное среди IT-сообщества." />,
      },
      {
        path: "/search",
        element: <PlaceholderPage titleKey="nav.search" fallbackTitle="Search" description="Поиск по людям, постам, клубам и хештегам." />,
      },
      {
        path: "/clubs",
        element: <PlaceholderPage titleKey="nav.clubs" fallbackTitle="Clubs" description="IT-сообщества: Python Kazakhstan, AI Engineers, Frontend и др." />,
      },
      {
        path: "/projects",
        element: <PlaceholderPage titleKey="nav.projects" fallbackTitle="Projects" description="Витрина проектов — GitHub, demo, технологии." />,
      },
      {
        path: "/messages",
        element: <PlaceholderPage titleKey="nav.messages" fallbackTitle="Messages" description="Личные сообщения и каналы клубов (WebSocket-ready)." />,
      },
      {
        path: "/notifications",
        element: <PlaceholderPage titleKey="nav.notifications" fallbackTitle="Notifications" description="Лайки, комментарии, подписки, упоминания." />,
      },
      {
        path: "/profile",
        element: <PlaceholderPage titleKey="nav.profile" fallbackTitle="Profile" description="Твой профиль: аватар, bio, навыки, проекты." />,
      },
      {
        path: "/settings",
        element: <PlaceholderPage titleKey="nav.settings" fallbackTitle="Settings" description="Язык, тема, приватность — появятся в STEP 13." />,
      },
      { path: "*", element: <NotFoundPage /> },
    ],
  },
]);

export function App() {
  return <RouterProvider router={router} />;
}
