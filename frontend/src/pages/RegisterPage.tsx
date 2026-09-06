import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Link, useNavigate } from "react-router-dom";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { authApi } from "@/api/auth";
import { ApiError } from "@/api/client";
import { useQueryClient } from "@tanstack/react-query";

const schema = z.object({
  username: z.string().min(3).max(50).regex(/^[a-zA-Z0-9_]+$/),
  email: z.string().email(),
  password: z.string().min(8).max(128),
  display_name: z.string().max(100).optional(),
});

type FormValues = z.infer<typeof schema>;

export function RegisterPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const qc = useQueryClient();
  const [serverError, setServerError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  const onSubmit = async (values: FormValues) => {
    setServerError(null);
    try {
      await authApi.register(values);
      await qc.invalidateQueries({ queryKey: ["auth", "me"] });
      navigate("/", { replace: true });
    } catch (e) {
      const err = e as ApiError;
      setServerError(err.message);
    }
  };

  const [demoLoading, setDemoLoading] = useState(false);
  const onDemo = async () => {
    setDemoLoading(true);
    setServerError(null);
    try {
      await authApi.demo();
      await qc.invalidateQueries({ queryKey: ["auth", "me"] });
      navigate("/", { replace: true });
    } catch (e) {
      const err = e as ApiError;
      setServerError(err.message);
    } finally {
      setDemoLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-md space-y-6 pt-6">
      <Card>
        <CardHeader>
          <CardTitle>{t("auth.registerTitle")}</CardTitle>
          <CardDescription>{t("auth.registerDesc")}</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
            <div className="space-y-1.5">
              <label htmlFor="reg-username" className="text-sm font-medium">{t("auth.username")}</label>
              <input
                id="reg-username"
                {...register("username")}
                placeholder={t("auth.usernamePlaceholder")}
                autoComplete="username"
                className="w-full rounded-xl border bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring focus-visible:ring-2"
              />
              {errors.username && <p className="text-xs text-red-500" role="alert">{errors.username.message}</p>}
            </div>
            <div className="space-y-1.5">
              <label htmlFor="reg-email" className="text-sm font-medium">{t("auth.email")}</label>
              <input id="reg-email" {...register("email")} placeholder="you@example.com" autoComplete="email" className="w-full rounded-xl border bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring focus-visible:ring-2" />
              {errors.email && <p className="text-xs text-red-500" role="alert">{errors.email.message}</p>}
            </div>
            <div className="space-y-1.5">
              <label htmlFor="reg-password" className="text-sm font-medium">{t("auth.password")}</label>
              <input id="reg-password" {...register("password")} type="password" placeholder={t("auth.passwordHint")} autoComplete="new-password" className="w-full rounded-xl border bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring focus-visible:ring-2" />
              {errors.password && <p className="text-xs text-red-500" role="alert">{errors.password.message}</p>}
            </div>
            <div className="space-y-1.5">
              <label htmlFor="reg-display" className="text-sm font-medium">{t("auth.displayNameOptional")}</label>
              <input id="reg-display" {...register("display_name")} placeholder={t("auth.displayNamePlaceholder")} className="w-full rounded-xl border bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring focus-visible:ring-2" />
            </div>
            {serverError && <p className="rounded-xl bg-red-50 p-3 text-xs text-red-700 dark:bg-red-950/30 dark:text-red-300" role="alert">{serverError}</p>}
            <Button type="submit" className="w-full" disabled={isSubmitting} aria-busy={isSubmitting}>
              {isSubmitting ? t("auth.creatingAccount") : t("auth.signUpAction")}
            </Button>
          </form>
          <p className="mt-4 text-center text-sm text-muted-foreground">
            {t("auth.hasAccount")}{" "}
            <Link to="/login" className="font-medium text-foreground underline focus-visible:ring-2 focus-visible:ring-ring rounded">
              {t("auth.signIn")}
            </Link>
          </p>
        </CardContent>
      </Card>

      <Card className="border-dashed">
        <CardContent className="p-4 space-y-3">
          <div className="text-center space-y-1">
            <p className="text-sm font-medium">Попробовать без регистрации</p>
            <p className="text-xs text-muted-foreground">Регистрация не требуется — откроется готовый демонстрационный аккаунт. Есть полный вход и регистрация — демо позволяет сразу посмотреть платформу без создания аккаунта.</p>
          </div>
          <Button variant="outline" className="w-full" onClick={onDemo} disabled={demoLoading} aria-label="Войти в демо">
            {demoLoading ? "Загрузка..." : "Войти в демо"}
          </Button>
          <p className="text-center text-xs text-muted-foreground">Демо: <span className="font-medium">demo</span> · готовая лента, проекты, клубы</p>
        </CardContent>
      </Card>
    </div>
  );
}
