import { useTranslation } from "react-i18next";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Construction, Sparkles } from "lucide-react";

export function PlaceholderPage({
  titleKey,
  fallbackTitle,
  description,
}: {
  titleKey: string;
  fallbackTitle: string;
  description: string;
}) {
  const { t } = useTranslation();
  const title = t(titleKey, fallbackTitle);
  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-foreground text-background">
          <Construction className="h-5 w-5" />
        </div>
        <div>
          <h1 className="text-xl font-semibold tracking-tight">{title}</h1>
          <p className="text-sm text-muted-foreground">{description}</p>
        </div>
        <Badge className="ml-auto">STEP 1 — заглушка</Badge>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Sparkles className="h-4 w-4" /> Скоро здесь будет: {title.toLowerCase()}
          </CardTitle>
          <CardDescription>
            Архитектура готова — страница подключена к роутеру и i18n. Контент появится в следующих STEP без переписывания foundation.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex gap-2">
          <Button variant="outline" size="sm" disabled>
            {t("common.comingSoon", "Скоро")}
          </Button>
        </CardContent>
      </Card>

      <div className="rounded-2xl border border-dashed p-6 text-center text-sm text-muted-foreground">
        Feed · Clubs · Messages · Projects — всё это будет здесь, но STEP 1 — только foundation.
      </div>
    </div>
  );
}
