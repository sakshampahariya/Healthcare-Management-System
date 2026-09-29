import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { TestTube2, Building2, Search, Calendar, Clock, AlertCircle } from "lucide-react";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { centresApi, bookingsApi, DiagnosticCentre, DiagnosticTest } from "@/services/api";

interface TestWithCentre extends DiagnosticTest {
  centreName: string;
  centreLocation: string;
}

export const Tests: React.FC = () => {
  const navigate = useNavigate();
  const [tests, setTests] = useState<TestWithCentre[]>([]);
  const [centres, setCentres] = useState<DiagnosticCentre[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [loading, setLoading] = useState(true);

  // Booking Modal State
  const [selectedTest, setSelectedTest] = useState<TestWithCentre | null>(null);
  const [appointmentDate, setAppointmentDate] = useState("");
  const [appointmentTime, setAppointmentTime] = useState("10:00");
  const [bookingLoading, setBookingLoading] = useState(false);
  const [bookingError, setBookingError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAllTests = async () => {
      try {
        const centresRes = await centresApi.list(1, 100);
        if (centresRes.success && centresRes.data) {
          setCentres(centresRes.data);
          const accumulatedTests: TestWithCentre[] = [];

          // Fetch full test list per centre
          for (const centre of centresRes.data) {
            try {
              const centreDetailRes = await centresApi.get(centre.id);
              if (centreDetailRes.success && centreDetailRes.data?.tests) {
                centreDetailRes.data.tests.forEach((test) => {
                  accumulatedTests.push({
                    ...test,
                    centreName: centre.name,
                    centreLocation: centre.location,
                  });
                });
              }
            } catch (e) {
              console.error(`Failed to fetch tests for centre ${centre.id}`, e);
            }
          }
          setTests(accumulatedTests);
        }
      } catch (err) {
        console.error("Failed to load tests catalogue:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchAllTests();
  }, []);

  const filteredTests = tests.filter(
    (t) =>
      t.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      t.centreName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (t.description && t.description.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const handleBookTest = async () => {
    if (!selectedTest || !appointmentDate) {
      setBookingError("Please select a date for your appointment.");
      return;
    }

    setBookingError(null);
    setBookingLoading(true);

    try {
      const fullDatetime = new Date(`${appointmentDate}T${appointmentTime}:00Z`).toISOString();
      const res = await bookingsApi.create({
        test_id: selectedTest.id,
        centre_id: selectedTest.centre_id,
        appointment_datetime: fullDatetime,
      });

      if (res.success && res.data) {
        setSelectedTest(null);
        navigate(`/payment/${res.data.id}`);
      }
    } catch (err: any) {
      setBookingError(err.response?.data?.error?.message || err.message || "Failed to create booking.");
    } finally {
      setBookingLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Section */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b pb-5">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Diagnostic Tests & Scans</h2>
          <p className="text-xs text-muted-foreground mt-1">
            Search across available medical procedures, blood profiles, and imaging tests.
          </p>
        </div>
        <div className="relative w-full md:w-80">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            type="search"
            placeholder="Search test name, procedure, or lab..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-9 text-xs"
          />
        </div>
      </div>

      {/* Tests Grid */}
      {loading ? (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3, 4].map((n) => (
            <Card key={n} className="animate-pulse">
              <CardHeader className="h-24 bg-muted/40 rounded-t-xl" />
              <CardContent className="p-6 space-y-2">
                <div className="h-4 w-2/3 bg-muted rounded" />
                <div className="h-3 w-1/2 bg-muted rounded" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {filteredTests.map((test) => (
            <Card key={`${test.centre_id}-${test.id}`} className="flex flex-col justify-between shadow-sm hover:border-primary/50 transition-colors">
              <CardHeader>
                <div className="flex items-start justify-between gap-2">
                  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-blue-50 text-blue-600">
                    <TestTube2 className="h-5 w-5" />
                  </div>
                  <span className="text-lg font-extrabold text-blue-600">${test.price}</span>
                </div>
                <CardTitle className="text-base font-bold mt-2 leading-snug">{test.name}</CardTitle>
                <CardDescription className="text-xs text-muted-foreground mt-1 line-clamp-2">
                  {test.description || "Standard diagnostic test profile."}
                </CardDescription>
              </CardHeader>

              <CardContent className="py-2 space-y-2">
                <div className="flex items-center gap-2 text-xs text-slate-700 bg-slate-50 p-2 rounded-lg border">
                  <Building2 className="h-4 w-4 text-primary shrink-0" />
                  <div className="truncate">
                    <span className="font-semibold">{test.centreName}</span>
                    <span className="text-[11px] text-muted-foreground block truncate">{test.centreLocation}</span>
                  </div>
                </div>
              </CardContent>

              <CardFooter className="pt-3 border-t flex justify-between items-center">
                <Badge variant="outline" className="text-[10px]">
                  Fast Report
                </Badge>
                <Button
                  size="sm"
                  onClick={() => {
                    setSelectedTest(test);
                    const tomorrow = new Date();
                    tomorrow.setDate(tomorrow.getDate() + 1);
                    setAppointmentDate(tomorrow.toISOString().split("T")[0]);
                  }}
                  className="text-xs font-semibold"
                >
                  Book Now
                </Button>
              </CardFooter>
            </Card>
          ))}

          {filteredTests.length === 0 && (
            <div className="col-span-full text-center py-12 bg-white rounded-xl border">
              <TestTube2 className="h-10 w-10 text-muted-foreground mx-auto mb-2" />
              <h3 className="font-semibold text-sm">No diagnostic tests found</h3>
              <p className="text-xs text-muted-foreground mt-1">Try searching with a different keyword</p>
            </div>
          )}
        </div>
      )}

      {/* Booking Dialog Modal */}
      <Dialog open={!!selectedTest} onOpenChange={() => setSelectedTest(null)}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="text-lg font-bold">Book Test Appointment</DialogTitle>
            <DialogDescription className="text-xs">
              Schedule your appointment for <span className="font-semibold text-foreground">{selectedTest?.name}</span>.
            </DialogDescription>
          </DialogHeader>

          {bookingError && (
            <div className="flex items-center gap-2 rounded-lg border border-rose-200 bg-rose-50 p-3 text-xs text-rose-800">
              <AlertCircle className="h-4 w-4 shrink-0 text-rose-600" />
              <span>{bookingError}</span>
            </div>
          )}

          <div className="space-y-4 py-2">
            <div className="rounded-lg bg-blue-50 p-3 border border-blue-100 flex justify-between items-center">
              <div>
                <p className="text-xs font-semibold text-blue-900">{selectedTest?.name}</p>
                <p className="text-[11px] text-blue-700">{selectedTest?.centreName}</p>
              </div>
              <span className="text-base font-bold text-blue-800">${selectedTest?.price}</span>
            </div>

            <div className="space-y-2">
              <Label htmlFor="date-modal" className="text-xs font-semibold">
                Select Date
              </Label>
              <div className="relative">
                <Calendar className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  id="date-modal"
                  type="date"
                  value={appointmentDate}
                  onChange={(e) => setAppointmentDate(e.target.value)}
                  className="pl-9 text-xs"
                  required
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="time-modal" className="text-xs font-semibold">
                Select Time Slot
              </Label>
              <div className="relative">
                <Clock className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  id="time-modal"
                  type="time"
                  value={appointmentTime}
                  onChange={(e) => setAppointmentTime(e.target.value)}
                  className="pl-9 text-xs"
                  required
                />
              </div>
            </div>
          </div>

          <DialogFooter className="gap-2 sm:gap-0">
            <Button variant="outline" size="sm" onClick={() => setSelectedTest(null)} disabled={bookingLoading}>
              Cancel
            </Button>
            <Button size="sm" onClick={handleBookTest} disabled={bookingLoading}>
              {bookingLoading ? "Confirming..." : "Confirm & Proceed to Payment"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};
