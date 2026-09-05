import { useTranslation } from "react-i18next";
import { useTheme } from "@/stores/theme";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Globe, Sun, Moon, Monitor } from "lucide-react";

export function SettingsPage() {
  const { t, i18n } = useTranslation();
  const { theme, setTheme } = useTheme();

  const langs = [
    { code: "ru", label: t("settings.russian") },
    { code: "kk", label: t("settings.kazakh") },
    { code: "en", label: t("settings.english") },
  ] as const;

  const themes = [
    { v: "light" as const, label: t("settings.light"), icon: Sun },
    { v: "dark" as const, label: t("settings.dark"), icon: Moon },
    { v: "system" as const, label: t("settings.system"), icon: Monitor },
  ];

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h1 className="text-xl font-semibold">{t("settings.title")}</h1>
        <p className="text-sm text-muted-foreground">{t("settings.subtitle")}</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base"><Globe className="h-4 w-4" /> {t("settings.language")}</CardTitle>
          <CardDescription>{t("settings.languageDesc")}</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-2">
          {langs.map((l) => (
            <Button
              key={l.code}
              variant={i18n.language?.startsWith(l.code) ? "default" : "outline"}
              size="sm"
              onClick={() => i18n.changeLanguage(l.code)}
              aria-label={`${t("a11y.language")}: ${l.label}`}
              aria-pressed={i18n.language?.startsWith(l.code)}
            >
              {l.label}
            </Button>
          ))}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base"><Sun className="h-4 w-4" /> {t("settings.theme")}</CardTitle>
          <CardDescription>{t("settings.themeDesc")}</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-2">
          {themes.map((th) => {
            const Icon = th.icon;
            return (
              <Button
                key={th.v}
                variant={theme === th.v ? "default" : "outline"}
                size="sm"
                onClick={() => setTheme(th.v)}
                aria-label={`${t("a11y.theme")}: ${th.label}`}
                aria-pressed={theme === th.v}
              >
                <Icon className="h-4 w-4 mr-1.5" /> {th.label}
              </Button>
            );
          })}
        </CardContent>
      </Card>
    </div>
  );
}
