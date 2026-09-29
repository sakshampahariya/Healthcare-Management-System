import React from "react";
import { User, Mail, Calendar, ShieldCheck, LogOut, Activity, Key } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { useAuth } from "@/context/AuthContext";

export const Profile: React.FC = () => {
  const { user, token, logout } = useAuth();

  const getInitials = (name?: string) => {
    if (!name) return "U";
    return name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase()
      .substring(0, 2);
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="border-b pb-4">
        <h2 className="text-2xl font-bold tracking-tight">Account & Profile Settings</h2>
        <p className="text-xs text-muted-foreground mt-1">
          Manage your patient account details, security credentials, and preferences.
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        {/* User Card */}
        <Card className="md:col-span-1 shadow-sm text-center">
          <CardHeader className="pb-4">
            <Avatar className="h-20 w-20 mx-auto shadow-sm ring-4 ring-blue-50">
              <AvatarFallback className="bg-primary text-primary-foreground font-bold text-xl">
                {getInitials(user?.name)}
              </AvatarFallback>
            </Avatar>
            <CardTitle className="text-lg font-bold mt-3">{user?.name}</CardTitle>
            <CardDescription className="text-xs text-muted-foreground">{user?.email}</CardDescription>
            <div className="pt-2">
              <Badge variant="outline" className="text-[10px] bg-blue-50 text-blue-700 border-blue-200">
                Verified Patient Account
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="border-t pt-4 text-xs space-y-3">
            <div className="flex justify-between items-center text-muted-foreground">
              <span>Patient ID</span>
              <span className="font-mono font-bold text-foreground">#{user?.id}</span>
            </div>
            <div className="flex justify-between items-center text-muted-foreground">
              <span>Registered</span>
              <span className="font-semibold text-foreground">
                {user?.created_at ? new Date(user.created_at).toLocaleDateString() : "Active Member"}
              </span>
            </div>
          </CardContent>
        </Card>

        {/* Details & Security */}
        <div className="md:col-span-2 space-y-6">
          <Card className="shadow-sm">
            <CardHeader>
              <CardTitle className="text-base font-bold flex items-center gap-2">
                <User className="h-4 w-4 text-primary" /> Personal Information
              </CardTitle>
              <CardDescription className="text-xs">Your registered account details</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label className="text-xs text-muted-foreground font-medium">Full Name</label>
                  <div className="flex items-center gap-2 p-2.5 rounded-lg border bg-slate-50 text-xs font-semibold">
                    <User className="h-4 w-4 text-muted-foreground" />
                    <span>{user?.name}</span>
                  </div>
                </div>

                <div className="space-y-1">
                  <label className="text-xs text-muted-foreground font-medium">Email Address</label>
                  <div className="flex items-center gap-2 p-2.5 rounded-lg border bg-slate-50 text-xs font-semibold">
                    <Mail className="h-4 w-4 text-muted-foreground" />
                    <span>{user?.email}</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Security & Authentication */}
          <Card className="shadow-sm">
            <CardHeader>
              <CardTitle className="text-base font-bold flex items-center gap-2">
                <ShieldCheck className="h-4 w-4 text-emerald-600" /> Authentication & Token
              </CardTitle>
              <CardDescription className="text-xs">JSON Web Token (JWT) Authorization status</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="rounded-lg border p-3 bg-slate-50 space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-semibold flex items-center gap-1.5 text-slate-700">
                    <Key className="h-3.5 w-3.5 text-primary" /> Active Bearer Token
                  </span>
                  <Badge variant="success">Authenticated</Badge>
                </div>
                <p className="font-mono text-[10px] text-muted-foreground truncate bg-white p-2 rounded border">
                  {token ? `Bearer ${token}` : "No token active"}
                </p>
              </div>

              <div className="pt-2">
                <Button
                  variant="destructive"
                  onClick={logout}
                  className="w-full gap-2 text-xs font-semibold"
                >
                  <LogOut className="h-4 w-4" /> Log Out of Account
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};
