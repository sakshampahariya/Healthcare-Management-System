import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Building2, MapPin, Search, TestTube2, ChevronRight } from "lucide-react";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { centresApi, DiagnosticCentre } from "@/services/api";

export const DiagnosticCentres: React.FC = () => {
  const [centres, setCentres] = useState<DiagnosticCentre[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCentres = async () => {
      try {
        const res = await centresApi.list(1, 100);
        if (res.success && res.data) {
          setCentres(res.data);
        }
      } catch (err) {
        console.error("Failed to load diagnostic centres:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchCentres();
  }, []);

  const filteredCentres = centres.filter(
    (c) =>
      c.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.location.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Header Section */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b pb-5">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Diagnostic Centres</h2>
          <p className="text-xs text-muted-foreground mt-1">
            Browse verified lab locations, radiology centres, and health checkup clinics.
          </p>
        </div>
        <div className="relative w-full md:w-80">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            type="search"
            placeholder="Search by centre name or location..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-9 text-xs"
          />
        </div>
      </div>

      {/* Grid of Centres */}
      {loading ? (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3].map((n) => (
            <Card key={n} className="animate-pulse">
              <CardHeader className="h-28 bg-muted/40 rounded-t-xl" />
              <CardContent className="p-6 space-y-2">
                <div className="h-4 w-2/3 bg-muted rounded" />
                <div className="h-3 w-1/2 bg-muted rounded" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {filteredCentres.map((centre) => (
            <Card key={centre.id} className="flex flex-col justify-between shadow-sm hover:shadow-md transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between gap-2">
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-blue-50 text-blue-600">
                    <Building2 className="h-5 w-5" />
                  </div>
                  <Badge variant="outline" className="text-[10px] font-normal">
                    Accredited
                  </Badge>
                </div>
                <CardTitle className="text-base font-bold mt-3 leading-snug">{centre.name}</CardTitle>
                <CardDescription className="flex items-center gap-1.5 text-xs text-muted-foreground mt-1">
                  <MapPin className="h-3.5 w-3.5 shrink-0 text-slate-500" />
                  <span className="truncate">{centre.location}</span>
                </CardDescription>
              </CardHeader>

              <CardContent className="py-2 text-xs text-muted-foreground">
                <div className="flex items-center gap-2 bg-slate-50 p-2.5 rounded-lg border text-slate-700">
                  <TestTube2 className="h-4 w-4 text-primary shrink-0" />
                  <span>Comprehensive diagnostic tests available</span>
                </div>
              </CardContent>

              <CardFooter className="pt-3 border-t flex justify-between items-center">
                <span className="text-[11px] text-muted-foreground font-medium">ID #{centre.id}</span>
                <Link to={`/centres/${centre.id}`}>
                  <Button size="sm" className="gap-1.5 text-xs">
                    View Tests & Details <ChevronRight className="h-3.5 w-3.5" />
                  </Button>
                </Link>
              </CardFooter>
            </Card>
          ))}

          {filteredCentres.length === 0 && (
            <div className="col-span-full text-center py-12 bg-white rounded-xl border">
              <Building2 className="h-10 w-10 text-muted-foreground mx-auto mb-2" />
              <h3 className="font-semibold text-sm">No diagnostic centres found</h3>
              <p className="text-xs text-muted-foreground mt-1">Try adjusting your search criteria</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
