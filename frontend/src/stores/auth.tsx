import React, { createContext, useContext } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { authApi, UserRead } from "@/api/auth";
import { ApiError } from "@/api/client";

type AuthState = {
  user: UserRead | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  error: Error | null;
  refetch: () => void;
  logout: () => Promise<void>;
};

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const qc = useQueryClient();
  const query = useQuery<UserRead, ApiError>({
    queryKey: ["auth", "me"],
    queryFn: () => authApi.me(),
    retry: false,
    staleTime: 5 * 60 * 1000,
  });

  const logout = async () => {
    try {
      await authApi.logout();
    } finally {
      qc.setQueryData(["auth", "me"], null);
      qc.invalidateQueries({ queryKey: ["auth", "me"] });
    }
  };

  const state: AuthState = {
    user: query.data ?? null,
    isLoading: query.isPending,
    isAuthenticated: !!query.data,
    error: query.error as Error | null,
    refetch: query.refetch as unknown as () => void,
    logout,
  };

  return <AuthContext.Provider value={state}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be inside AuthProvider");
  return ctx;
}

export function useCurrentUser() {
  return useAuth();
}
