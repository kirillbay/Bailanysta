import { createBrowserRouter, RouterProvider, Navigate } from "react-router-dom";
import { Suspense, lazy } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { RequireAuth } from "@/components/RequireAuth";
import { NotFoundPage } from "@/pages/NotFoundPage";
import { Skeleton } from "@/components/ui/skeleton";
import { LoginPage } from "@/pages/LoginPage";
import { RegisterPage } from "@/pages/RegisterPage";

const FeedPage = lazy(() => import("@/pages/FeedPage").then(m => ({ default: m.FeedPage })));
const SearchPage = lazy(() => import("@/pages/SearchPage").then(m => ({ default: m.SearchPage })));
const HashtagPage = lazy(() => import("@/pages/HashtagPage").then(m => ({ default: m.HashtagPage })));
const ClubsPage = lazy(() => import("@/pages/ClubsPage").then(m => ({ default: m.ClubsPage })));
const ClubPage = lazy(() => import("@/pages/ClubPage").then(m => ({ default: m.ClubPage })));
const ClubChannelPage = lazy(() => import("@/pages/ClubChannelPage").then(m => ({ default: m.ClubChannelPage })));
const NotificationsPage = lazy(() => import("@/pages/NotificationsPage").then(m => ({ default: m.NotificationsPage })));
const ProjectsPage = lazy(() => import("@/pages/ProjectsPage").then(m => ({ default: m.ProjectsPage })));
const ProjectDetailPage = lazy(() => import("@/pages/ProjectDetailPage").then(m => ({ default: m.ProjectDetailPage })));
const ProfilePage = lazy(() => import("@/pages/ProfilePage").then(m => ({ default: m.ProfilePage })));
const PostDetailPage = lazy(() => import("@/pages/PostDetailPage").then(m => ({ default: m.PostDetailPage })));
const BookmarksPage = lazy(() => import("@/pages/BookmarksPage").then(m => ({ default: m.BookmarksPage })));
const SettingsPage = lazy(() => import("@/pages/SettingsPage").then(m => ({ default: m.SettingsPage })));
const MessagesPage = lazy(() => import("@/pages/MessagesPage").then(m => ({ default: m.MessagesPage })));

function Fallback() {
  return <div className="mx-auto max-w-2xl p-6"><Skeleton className="h-32 w-full rounded-2xl" /></div>;
}

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
      { path: "/", element: <Suspense fallback={<Fallback />}><FeedPage /></Suspense> },
      { path: "/explore", element: <Navigate to="/search" replace /> },
      { path: "/search", element: <Suspense fallback={<Fallback />}><SearchPage /></Suspense> },
      { path: "/hashtags/:name", element: <Suspense fallback={<Fallback />}><HashtagPage /></Suspense> },
      { path: "/clubs", element: <Suspense fallback={<Fallback />}><ClubsPage /></Suspense> },
      { path: "/clubs/:slug", element: <Suspense fallback={<Fallback />}><ClubPage /></Suspense> },
      { path: "/clubs/:slug/channels/:channelSlug", element: <Suspense fallback={<Fallback />}><ClubChannelPage /></Suspense> },
      { path: "/projects", element: <Suspense fallback={<Fallback />}><ProjectsPage /></Suspense> },
      { path: "/projects/:projectId", element: <Suspense fallback={<Fallback />}><ProjectDetailPage /></Suspense> },
      { path: "/messages", element: <Suspense fallback={<Fallback />}><MessagesPage /></Suspense> },
      { path: "/notifications", element: <Suspense fallback={<Fallback />}><NotificationsPage /></Suspense> },
      { path: "/profile", element: <Suspense fallback={<Fallback />}><ProfilePage /></Suspense> },
      { path: "/profile/:username", element: <Suspense fallback={<Fallback />}><ProfilePage /></Suspense> },
      { path: "/posts/:postId", element: <Suspense fallback={<Fallback />}><PostDetailPage /></Suspense> },
      { path: "/bookmarks", element: <Suspense fallback={<Fallback />}><BookmarksPage /></Suspense> },
      { path: "/settings", element: <Suspense fallback={<Fallback />}><SettingsPage /></Suspense> },
      { path: "*", element: <NotFoundPage /> },
    ],
  },
]);

export function App() {
  return <RouterProvider router={router} />;
}
