import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center gap-4 text-center">
      <div className="text-6xl font-black tracking-tighter text-muted-foreground/20">404</div>
      <h1 className="text-xl font-semibold">Страница не найдена</h1>
      <p className="max-w-sm text-sm text-muted-foreground">Проверь адрес или вернись на главную.</p>
      <Link to="/" className="rounded-xl bg-foreground px-4 py-2 text-sm text-background">
        На главную
      </Link>
    </div>
  );
}
