import React from "react";
import { Outlet, useLocation } from "react-router-dom";
import { SidebarProvider } from "@/components/ui/sidebar";
import { AppSidebar } from "./AppSidebar";
import { Bell, Search } from "lucide-react";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/context/AuthContext";

export const MainLayout: React.FC = () => {
  const location = useLocation();
  const { user } = useAuth();

  const getPageTitle = () => {
    const path = location.pathname;
    if (path.startsWith("/dashboard")) return "Dashboard Overview";
    if (path.startsWith("/centres")) return "Diagnostic Centres";
    if (path.startsWith("/tests")) return "Diagnostic Tests & Scans";
    if (path.startsWith("/bookings")) return "My Bookings";
    if (path.startsWith("/payment")) return "Simulated Payment Gateway";
    if (path.startsWith("/profile")) return "Account & Profile Settings";
    return "EVE Healthcare";
  };

  return (
    <SidebarProvider>
      <div className="flex min-h-screen w-full">
        <AppSidebar />
        <div className="flex flex-1 flex-col overflow-x-hidden">
          {/* Top Bar */}
          <header className="sticky top-0 z-20 flex h-16 w-full items-center justify-between border-b bg-background/95 px-6 backdrop-blur">
            <h1 className="text-xl font-bold tracking-tight text-slate-900 dark:text-white">
              {getPageTitle()}
            </h1>

            <div className="flex items-center gap-4">
              <div className="relative hidden md:block w-64">
                <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  type="search"
                  placeholder="Search centres, tests..."
                  className="pl-8 h-9 text-xs bg-muted/40"
                />
              </div>

              <div className="flex items-center gap-2 border-l pl-4">
                <div className="text-right hidden sm:block">
                  <p className="text-xs font-semibold leading-tight text-slate-800">{user?.name}</p>
                  <p className="text-[11px] text-muted-foreground">Patient</p>
                </div>
              </div>
            </div>
          </header>

          {/* Main Content Area */}
          <main className="flex-1 p-6 max-w-7xl w-full mx-auto">
            <Outlet />
          </main>
        </div>
      </div>
    </SidebarProvider>
  );
};
