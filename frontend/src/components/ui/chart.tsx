import * as React from "react";
import { ResponsiveContainer } from "recharts";
import { cn } from "@/lib/utils";

export interface ChartConfig {
  [key: string]: {
    label?: React.ReactNode;
    icon?: React.ComponentType;
    color?: string;
  };
}

interface ChartContainerProps extends React.HTMLAttributes<HTMLDivElement> {
  config: ChartConfig;
  children: React.ReactElement;
}

export const ChartContainer = React.forwardRef<HTMLDivElement, ChartContainerProps>(
  ({ config, className, children, ...props }, ref) => {
    // Generate CSS variables dynamically for chart colors
    const style = React.useMemo(() => {
      const colorStyles: Record<string, string> = {};
      Object.entries(config).forEach(([key, value]) => {
        if (value.color) {
          colorStyles[`--color-${key}`] = value.color;
        }
      });
      return colorStyles;
    }, [config]);

    return (
      <div
        ref={ref}
        style={style as React.CSSProperties}
        className={cn("flex aspect-video justify-center text-xs [&_.recharts-cartesian-axis-tick_text]:fill-muted-foreground", className)}
        {...props}
      >
        <ResponsiveContainer width="100%" height="100%">
          {children}
        </ResponsiveContainer>
      </div>
    );
  }
);
ChartContainer.displayName = "ChartContainer";

export function ChartTooltipContent({
  active,
  payload,
  label,
  indicator = "dot",
}: {
  active?: boolean;
  payload?: any[];
  label?: string;
  indicator?: "dot" | "line";
}) {
  if (!active || !payload?.length) {
    return null;
  }

  return (
    <div className="rounded-lg border bg-background p-2.5 shadow-md text-xs space-y-1">
      {label && <p className="font-semibold text-foreground">{label}</p>}
      <div className="space-y-1">
        {payload.map((item: any, idx: number) => (
          <div key={idx} className="flex items-center gap-2 text-muted-foreground">
            <span
              className={cn(
                "h-2 w-2 rounded-full",
                indicator === "dot" && "rounded-full",
                indicator === "line" && "h-0.5 w-3 rounded-none"
              )}
              style={{ backgroundColor: item.color || item.fill }}
            />
            <span className="font-medium text-foreground">{item.name}:</span>
            <span className="font-bold text-foreground">{item.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
