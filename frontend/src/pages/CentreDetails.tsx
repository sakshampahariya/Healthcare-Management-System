import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Building2, MapPin, TestTube2, ArrowLeft, Clock, Calendar, AlertCircle } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
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

export const CentreDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [centre, setCentre] = useState<DiagnosticCentre | null>(null);
  const [loading, setLoading] = useState(true);

  // Booking Modal State
  const [selectedTest, setSelectedTest] = useState<DiagnosticTest | null>(null);
  const [appointmentDate, setAppointmentDate] = useState("");
  const [appointmentTime, setAppointmentTime] = useState("10:00");
  const [bookingLoading, setBookingLoading] = useState(false);
  const [bookingError, setBookingError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    const fetchCentreDetails = async () => {
      try {
        const res = await centresApi.get(parseInt(id, 10));
        if (res.success && res.data) {
          setCentre(res.data);
        }
      } catch (err) {
        console.error("Failed to load centre details:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchCentreDetails();
  }, [id]);

  const handleBookTest = async () => {
    if (!selectedTest || !centre || !appointmentDate) {
      setBookingError("Please select a date for your appointment.");
      return;
    }

    setBookingError(null);
    setBookingLoading(true);

    try {
      // Combine date and time to ISO string
      const fullDatetime = new Date(`${appointmentDate}T${appointmentTime}:00Z`).toISOString();
      const res = await bookingsApi.create({
        test_id: selectedTest.id,
        centre_id: centre.id,
        appointment_datetime: fullDatetime,
      });

      if (res.success && res.data) {
        setSelectedTest(null);
        // Navigate directly to payment or booking details
        navigate(`/payment/${res.data.id}`);
      }
    } catch (err: any) {
      setBookingError(err.response?.data?.error?.message || err.message || "Failed to create booking.");
    } finally {
      setBookingLoading(false);
    }
  };

  if (loading) {
    return <div className="p-8 text-center text-xs text-muted-foreground">Loading centre information...</div>;
  }

  if (!centre) {
    return (
      <div className="p-8 text-center space-y-4">
        <h3 className="text-lg font-bold">Centre Not Found</h3>
        <Button onClick={() => navigate("/centres")} size="sm">
          Back to Centres
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Back Button */}
      <Button variant="ghost" size="sm" onClick={() => navigate("/centres")} className="gap-2 text-xs">
        <ArrowLeft className="h-4 w-4" /> Back to Diagnostic Centres
      </Button>

      {/* Centre Overview Card */}
      <Card className="shadow-sm border-blue-100">
        <CardHeader className="bg-slate-50/50 rounded-t-xl pb-6">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="flex items-start gap-4">
              <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-xl bg-primary text-primary-foreground shadow">
                <Building2 className="h-7 w-7" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <CardTitle className="text-2xl font-bold">{centre.name}</CardTitle>
                  <Badge variant="success">Active</Badge>
                </div>
                <CardDescription className="flex items-center gap-1.5 text-xs text-muted-foreground mt-1.5">
                  <MapPin className="h-4 w-4 text-primary shrink-0" />
                  <span className="font-medium text-slate-800">{centre.location}</span>
                </CardDescription>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Badge variant="outline" className="px-3 py-1 text-xs bg-white">
                Centre ID #{centre.id}
              </Badge>
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Available Diagnostic Tests */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-bold tracking-tight flex items-center gap-2">
            <TestTube2 className="h-5 w-5 text-primary" />
            Available Tests & Diagnostic Packages ({centre.tests?.length || 0})
          </h3>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          {centre.tests && centre.tests.length > 0 ? (
            centre.tests.map((test) => (
              <Card key={test.id} className="shadow-sm hover:border-primary/50 transition-colors">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between gap-2">
                    <CardTitle className="text-base font-bold">{test.name}</CardTitle>
                    <span className="text-lg font-extrabold text-blue-600">${test.price}</span>
                  </div>
                  {test.description && (
                    <CardDescription className="text-xs mt-1 leading-relaxed">
                      {test.description}
                    </CardDescription>
                  )}
                </CardHeader>
                <CardContent className="pt-0 flex justify-between items-center">
                  <span className="text-[11px] text-muted-foreground flex items-center gap-1">
                    <Clock className="h-3.5 w-3.5" /> Fast 24h digital report
                  </span>
                  <Button
                    size="sm"
                    onClick={() => {
                      setSelectedTest(test);
                      // Default appointment date to tomorrow
                      const tomorrow = new Date();
                      tomorrow.setDate(tomorrow.getDate() + 1);
                      setAppointmentDate(tomorrow.toISOString().split("T")[0]);
                    }}
                    className="text-xs font-semibold"
                  >
                    Book This Test
                  </Button>
                </CardContent>
              </Card>
            ))
          ) : (
            <div className="col-span-full py-8 text-center text-xs text-muted-foreground border rounded-xl bg-white">
              No tests currently listed for this centre.
            </div>
          )}
        </div>
      </div>

      {/* Booking Dialog Modal */}
      <Dialog open={!!selectedTest} onOpenChange={() => setSelectedTest(null)}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="text-lg font-bold">Book Test Appointment</DialogTitle>
            <DialogDescription className="text-xs">
              Schedule your appointment for <span className="font-semibold text-foreground">{selectedTest?.name}</span> at{" "}
              <span className="font-semibold text-foreground">{centre.name}</span>.
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
                <p className="text-[11px] text-blue-700">{centre.name}</p>
              </div>
              <span className="text-base font-bold text-blue-800">${selectedTest?.price}</span>
            </div>

            <div className="space-y-2">
              <Label htmlFor="date" className="text-xs font-semibold">
                Select Date
              </Label>
              <div className="relative">
                <Calendar className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  id="date"
                  type="date"
                  value={appointmentDate}
                  onChange={(e) => setAppointmentDate(e.target.value)}
                  className="pl-9 text-xs"
                  required
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="time" className="text-xs font-semibold">
                Select Time Slot
              </Label>
              <div className="relative">
                <Clock className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  id="time"
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
