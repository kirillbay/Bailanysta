import { useQuery } from "@tanstack/react-query";
import { api } from "@/api/client";

export function useHealth() {
  return useQuery({
    queryKey: ["health"],
    queryFn: () => api.health(),
    retry: 1,
    staleTime: 30_000,
  });
}
