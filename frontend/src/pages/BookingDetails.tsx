import React, { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import {
  ArrowLeft,
  Calendar,
  Clock,
  Building2,
  TestTube2,
  DollarSign,
  CreditCard,
  XCircle,
  CheckCircle2,
  AlertCircle,
  FileText,
} from "lucide-react";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  bookingsApi,
  testsApi,
  centresApi,
  Booking,
  DiagnosticTest,
  DiagnosticCentre,
} from "@/services/api";

export const BookingDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [booking, setBooking] = useState<Booking | null>(null);
  const [test, setTest] = useState<DiagnosticTest | null>(null);
  const [centre, setCentre] = useState<DiagnosticCentre | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;

    const fetchDetails = async () => {
      try {
        const bookingRes = await bookingsApi.get(parseInt(id, 10));
        if (bookingRes.success && bookingRes.data) {
          const b = bookingRes.data;
          setBooking(b);

          // Fetch associated test and centre
          const [testRes, centreRes] = await Promise.all([
            testsApi.get(b.test_id),
            centresApi.get(b.centre_id),
          ]);

          if (testRes.success) setTest(testRes.data);
          if (centreRes.success) setCentre(centreRes.data);
        }
      } catch (err) {
        console.error("Failed to load booking details:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchDetails();
  }, [id]);

  const handleCancelBooking = async () => {
    if (!booking) return;
    if (!window.confirm("Are you sure you want to cancel this booking?")) return;

    try {
      const res = await bookingsApi.cancel(booking.id);
      if (res.success && res.data) {
        setBooking(res.data);
      }
    } catch (err: any) {
      alert(err.response?.data?.error?.message || "Failed to cancel booking");
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "CONFIRMED":
        return <Badge variant="success">Confirmed & Scheduled</Badge>;
      case "PENDING":
        return <Badge variant="warning">Awaiting Payment</Badge>;
      case "CANCELLED":
        return <Badge variant="destructive">Cancelled</Badge>;
      case "FAILED":
        return <Badge variant="destructive">Failed</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  if (loading) {
    return <div className="p-8 text-center text-xs text-muted-foreground">Loading booking details...</div>;
  }

  if (!booking) {
    return (
      <div className="p-8 text-center space-y-4">
        <h3 className="text-lg font-bold">Booking Not Found</h3>
        <Button onClick={() => navigate("/bookings")} size="sm">
          Back to Bookings
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Back Button */}
      <Button variant="ghost" size="sm" onClick={() => navigate("/bookings")} className="gap-2 text-xs">
        <ArrowLeft className="h-4 w-4" /> Back to My Bookings
      </Button>

      {/* Main Card */}
      <Card className="shadow-md">
        <CardHeader className="border-b bg-slate-50/50 pb-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-3">
                <CardTitle className="text-xl font-bold">Booking #{booking.id}</CardTitle>
                {getStatusBadge(booking.status)}
              </div>
              <CardDescription className="text-xs mt-1">
                Created on {new Date(booking.created_at).toLocaleString()}
              </CardDescription>
            </div>
            <div className="text-right">
              <span className="text-xs text-muted-foreground block">Total Amount</span>
              <span className="text-2xl font-extrabold text-blue-600">${booking.amount}</span>
            </div>
          </div>
        </CardHeader>

        <CardContent className="p-6 space-y-6">
          {/* Details Grid */}
          <div className="grid gap-6 md:grid-cols-2">
            {/* Test Details */}
            <div className="space-y-3 rounded-xl border p-4 bg-white shadow-xs">
              <div className="flex items-center gap-2 text-primary font-semibold text-sm">
                <TestTube2 className="h-4 w-4" /> Diagnostic Test Info
              </div>
              <div className="space-y-1 text-xs">
                <p className="font-bold text-slate-900 text-base">{test?.name || `Test #${booking.test_id}`}</p>
                <p className="text-muted-foreground leading-relaxed">
                  {test?.description || "Diagnostic procedure & laboratory examination."}
                </p>
              </div>
            </div>

            {/* Centre Location */}
            <div className="space-y-3 rounded-xl border p-4 bg-white shadow-xs">
              <div className="flex items-center gap-2 text-primary font-semibold text-sm">
                <Building2 className="h-4 w-4" /> Diagnostic Centre Info
              </div>
              <div className="space-y-1 text-xs">
                <p className="font-bold text-slate-900 text-base">{centre?.name || `Centre #${booking.centre_id}`}</p>
                <p className="text-muted-foreground">{centre?.location || "Centre location address"}</p>
              </div>
            </div>
          </div>

          {/* Appointment Datetime */}
          <div className="rounded-xl border border-blue-100 bg-blue-50/60 p-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-600 text-white">
                <Calendar className="h-5 w-5" />
              </div>
              <div>
                <p className="text-xs font-semibold text-blue-900">Scheduled Appointment Date</p>
                <p className="text-sm font-bold text-blue-950">
                  {new Date(booking.appointment_datetime).toLocaleString(undefined, {
                    dateStyle: "full",
                    timeStyle: "short",
                  })}
                </p>
              </div>
            </div>
          </div>

          {/* Timeline Status */}
          <div className="space-y-3 pt-2">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Booking Progress
            </h4>
            <div className="grid gap-3 sm:grid-cols-3">
              <div className="flex items-center gap-2.5 p-3 rounded-lg border bg-emerald-50/50 border-emerald-200">
                <CheckCircle2 className="h-4 w-4 text-emerald-600 shrink-0" />
                <span className="text-xs font-medium text-emerald-900">Booking Initiated</span>
              </div>

              <div
                className={`flex items-center gap-2.5 p-3 rounded-lg border ${
                  booking.status === "CONFIRMED"
                    ? "bg-emerald-50/50 border-emerald-200"
                    : booking.status === "PENDING"
                    ? "bg-amber-50/50 border-amber-200"
                    : "bg-slate-50 border-slate-200 opacity-60"
                }`}
              >
                {booking.status === "CONFIRMED" ? (
                  <CheckCircle2 className="h-4 w-4 text-emerald-600 shrink-0" />
                ) : (
                  <Clock className="h-4 w-4 text-amber-600 shrink-0" />
                )}
                <span className="text-xs font-medium">Payment ({booking.status})</span>
              </div>

              <div
                className={`flex items-center gap-2.5 p-3 rounded-lg border ${
                  booking.status === "CONFIRMED"
                    ? "bg-blue-50/50 border-blue-200"
                    : "bg-slate-50 border-slate-200 opacity-60"
                }`}
              >
                <FileText className="h-4 w-4 text-blue-600 shrink-0" />
                <span className="text-xs font-medium">Test Report Ready</span>
              </div>
            </div>
          </div>
        </CardContent>

        <CardFooter className="border-t bg-slate-50/50 p-4 flex justify-between items-center">
          <span className="text-xs text-muted-foreground">Updated: {new Date(booking.updated_at).toLocaleString()}</span>
          <div className="flex items-center gap-2">
            {booking.status === "PENDING" && (
              <>
                <Button variant="outline" size="sm" onClick={handleCancelBooking} className="text-xs text-rose-600 hover:bg-rose-50">
                  <XCircle className="h-4 w-4 mr-1.5" /> Cancel Booking
                </Button>
                <Link to={`/payment/${booking.id}`}>
                  <Button size="sm" className="gap-2 text-xs font-semibold shadow">
                    <CreditCard className="h-4 w-4" /> Proceed to Payment
                  </Button>
                </Link>
              </>
            )}
          </div>
        </CardFooter>
      </Card>
    </div>
  );
};
