import * as React from "react";
import { X, CheckCircle2, AlertCircle, Info } from "lucide-react";
import { cn } from "@/lib/utils";

export interface ToastProps {
  id?: string;
  title?: string;
  description?: string;
  type?: "success" | "error" | "info";
  onClose?: () => void;
}

export function Toast({ title, description, type = "info", onClose }: ToastProps) {
  return (
    <div
      className={cn(
        "flex w-full max-w-sm items-start gap-3 rounded-lg border p-4 shadow-lg transition-all bg-background text-foreground",
        type === "success" && "border-emerald-500/20 bg-emerald-50/90 dark:bg-emerald-950/40 text-emerald-900 dark:text-emerald-200",
        type === "error" && "border-rose-500/20 bg-rose-50/90 dark:bg-rose-950/40 text-rose-900 dark:text-rose-200",
        type === "info" && "border-blue-500/20 bg-blue-50/90 dark:bg-blue-950/40 text-blue-900 dark:text-blue-200"
      )}
    >
      {type === "success" && <CheckCircle2 className="h-5 w-5 text-emerald-600 shrink-0 mt-0.5" />}
      {type === "error" && <AlertCircle className="h-5 w-5 text-rose-600 shrink-0 mt-0.5" />}
      {type === "info" && <Info className="h-5 w-5 text-blue-600 shrink-0 mt-0.5" />}
      <div className="flex-1 space-y-1">
        {title && <h5 className="font-semibold text-sm leading-tight">{title}</h5>}
        {description && <p className="text-xs opacity-90 leading-normal">{description}</p>}
      </div>
      {onClose && (
        <button
          onClick={onClose}
          className="rounded-md p-1 opacity-70 hover:opacity-100 transition-opacity"
        >
          <X className="h-4 w-4" />
        </button>
      )}
    </div>
  );
}
