import { createBrowserRouter, RouterProvider } from "react-router-dom";
import { AppShell } from "@/components/layout/AppShell";
import { FeedPage } from "@/pages/FeedPage";
import { PlaceholderPage } from "@/pages/PlaceholderPage";
import { NotFoundPage } from "@/pages/NotFoundPage";
import { LoginPage } from "@/pages/LoginPage";
import { RegisterPage } from "@/pages/RegisterPage";
import { RequireAuth } from "@/components/RequireAuth";
import { ProfilePage } from "@/pages/ProfilePage";
import { PostDetailPage } from "@/pages/PostDetailPage";
import { BookmarksPage } from "@/pages/BookmarksPage";
import { SearchPage } from "@/pages/SearchPage";
import { HashtagPage } from "@/pages/HashtagPage";
import { ClubsPage } from "@/pages/ClubsPage";
import { ClubPage } from "@/pages/ClubPage";
import { ClubChannelPage } from "@/pages/ClubChannelPage";
import { NotificationsPage } from "@/pages/NotificationsPage";

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
      { path: "/search", element: <SearchPage /> },
      { path: "/hashtags/:name", element: <HashtagPage /> },
      { path: "/clubs", element: <ClubsPage /> },
      { path: "/clubs/:slug", element: <ClubPage /> },
      { path: "/clubs/:slug/channels/:channelSlug", element: <ClubChannelPage /> },
      {
        path: "/projects",
        element: <PlaceholderPage titleKey="nav.projects" fallbackTitle="Projects" description="Витрина проектов — GitHub, demo, технологии." />,
      },
      {
        path: "/messages",
        element: <PlaceholderPage titleKey="nav.messages" fallbackTitle="Messages" description="Личные сообщения и каналы клубов (WebSocket-ready)." />,
      },
      { path: "/notifications", element: <NotificationsPage /> },
      { path: "/profile", element: <ProfilePage /> },
      { path: "/profile/:username", element: <ProfilePage /> },
      { path: "/posts/:postId", element: <PostDetailPage /> },
      { path: "/bookmarks", element: <BookmarksPage /> },
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
