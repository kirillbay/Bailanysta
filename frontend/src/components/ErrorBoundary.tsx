import React from "react";

type Props = { children: React.ReactNode };
type State = { hasError: boolean; error?: Error };

export class ErrorBoundary extends React.Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    console.error("[ErrorBoundary]", error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex min-h-[60vh] flex-col items-center justify-center gap-4 p-8 text-center">
          <h2 className="text-xl font-semibold">Что-то пошло не так</h2>
          <p className="max-w-md text-sm text-muted-foreground">
            {this.state.error?.message ?? "Неизвестная ошибка приложения."}
          </p>
          <button
            onClick={() => this.setState({ hasError: false })}
            className="rounded-xl bg-foreground px-4 py-2 text-sm text-background"
          >
            Попробовать снова
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
