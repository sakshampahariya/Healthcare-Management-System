import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  CreditCard,
  CheckCircle2,
  XCircle,
  ShieldCheck,
  ArrowLeft,
  AlertCircle,
  DollarSign,
  Loader2,
} from "lucide-react";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { bookingsApi, paymentsApi, Booking } from "@/services/api";

export const SimulatedPayment: React.FC = () => {
  const { bookingId } = useParams<{ bookingId: string }>();
  const navigate = useNavigate();
  const [booking, setBooking] = useState<Booking | null>(null);
  const [simulateResult, setSimulateResult] = useState<"SUCCESS" | "FAILED">("SUCCESS");
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [paymentSuccess, setPaymentSuccess] = useState<boolean | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!bookingId) return;

    const fetchBooking = async () => {
      try {
        const res = await bookingsApi.get(parseInt(bookingId, 10));
        if (res.success && res.data) {
          setBooking(res.data);
          if (res.data.status === "CONFIRMED") {
            setPaymentSuccess(true);
          }
        }
      } catch (err) {
        console.error("Failed to load booking for payment:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchBooking();
  }, [bookingId]);

  const handleProcessPayment = async () => {
    if (!booking) return;

    setError(null);
    setProcessing(true);

    try {
      const res = await paymentsApi.create({
        booking_id: booking.id,
        simulate_result: simulateResult,
      });

      if (res.success) {
        if (res.data.booking_status === "CONFIRMED" || res.data.payment.status === "SUCCESS") {
          setPaymentSuccess(true);
        } else {
          setPaymentSuccess(false);
          setError("Simulated payment failed as requested.");
        }
      }
    } catch (err: any) {
      setPaymentSuccess(false);
      setError(err.response?.data?.error?.message || err.message || "Payment simulation failed.");
    } finally {
      setProcessing(false);
    }
  };

  if (loading) {
    return <div className="p-8 text-center text-xs text-muted-foreground">Loading payment environment...</div>;
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
    <div className="space-y-6 max-w-lg mx-auto">
      {/* Back link */}
      <Button variant="ghost" size="sm" onClick={() => navigate(`/bookings/${booking.id}`)} className="gap-2 text-xs">
        <ArrowLeft className="h-4 w-4" /> Back to Booking Details
      </Button>

      <Card className="shadow-lg border-blue-100">
        <CardHeader className="bg-gradient-to-r from-blue-700 to-indigo-700 text-white rounded-t-xl pb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <ShieldCheck className="h-6 w-6 text-blue-200" />
              <CardTitle className="text-lg font-bold">Simulated Payment Gateway</CardTitle>
            </div>
            <Badge className="bg-blue-800 text-blue-100 text-[10px] border-blue-600">Sandbox Mode</Badge>
          </div>
          <CardDescription className="text-blue-100 text-xs mt-1">
            Complete simulated checkout for Booking #{booking.id}
          </CardDescription>
        </CardHeader>

        <CardContent className="p-6 space-y-6">
          {/* Booking Summary Box */}
          <div className="rounded-xl bg-slate-50 border p-4 space-y-2">
            <div className="flex justify-between items-center text-xs text-muted-foreground">
              <span>Diagnostic Test Appointment</span>
              <span>Booking #{booking.id}</span>
            </div>
            <div className="flex justify-between items-center pt-2 border-t">
              <span className="font-semibold text-sm">Amount Due</span>
              <span className="text-2xl font-extrabold text-blue-700">${booking.amount}</span>
            </div>
          </div>

          {/* Payment Status Success Banner */}
          {paymentSuccess === true && (
            <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-center space-y-3">
              <div className="h-12 w-12 bg-emerald-600 text-white rounded-full flex items-center justify-center mx-auto shadow-sm">
                <CheckCircle2 className="h-7 w-7" />
              </div>
              <div>
                <h4 className="font-bold text-base text-emerald-950">Payment Successful!</h4>
                <p className="text-xs text-emerald-800 mt-1">
                  Your booking has been officially CONFIRMED and your appointment slot is reserved.
                </p>
              </div>
              <Button onClick={() => navigate(`/bookings/${booking.id}`)} className="w-full bg-emerald-700 hover:bg-emerald-800 text-xs mt-2">
                View Confirmed Booking
              </Button>
            </div>
          )}

          {/* Payment Simulation Form */}
          {paymentSuccess !== true && (
            <div className="space-y-4">
              {error && (
                <div className="flex items-center gap-2 rounded-lg border border-rose-200 bg-rose-50 p-3 text-xs text-rose-800">
                  <AlertCircle className="h-4 w-4 shrink-0 text-rose-600" />
                  <span>{error}</span>
                </div>
              )}

              <div className="space-y-2">
                <label className="text-xs font-semibold text-slate-700">Select Simulation Outcome:</label>
                <div className="grid grid-cols-2 gap-3">
                  <button
                    type="button"
                    onClick={() => setSimulateResult("SUCCESS")}
                    className={`flex flex-col items-center justify-center p-3 rounded-lg border transition-all text-xs font-medium ${
                      simulateResult === "SUCCESS"
                        ? "border-emerald-500 bg-emerald-50/80 text-emerald-900 shadow-xs ring-1 ring-emerald-500"
                        : "bg-white text-muted-foreground hover:bg-slate-50"
                    }`}
                  >
                    <CheckCircle2 className={`h-5 w-5 mb-1 ${simulateResult === "SUCCESS" ? "text-emerald-600" : "text-slate-400"}`} />
                    Simulate Success
                  </button>

                  <button
                    type="button"
                    onClick={() => setSimulateResult("FAILED")}
                    className={`flex flex-col items-center justify-center p-3 rounded-lg border transition-all text-xs font-medium ${
                      simulateResult === "FAILED"
                        ? "border-rose-500 bg-rose-50/80 text-rose-900 shadow-xs ring-1 ring-rose-500"
                        : "bg-white text-muted-foreground hover:bg-slate-50"
                    }`}
                  >
                    <XCircle className={`h-5 w-5 mb-1 ${simulateResult === "FAILED" ? "text-rose-600" : "text-slate-400"}`} />
                    Simulate Failure
                  </button>
                </div>
              </div>

              {/* Payment Card Visual */}
              <div className="rounded-xl border bg-gradient-to-r from-slate-900 to-slate-800 text-white p-4 shadow-md space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-[10px] tracking-wider uppercase font-semibold text-slate-400">EVE Test Payment</span>
                  <CreditCard className="h-5 w-5 text-blue-400" />
                </div>
                <div className="text-sm font-mono tracking-widest text-slate-200">
                  •••• •••• •••• 4242
                </div>
                <div className="flex justify-between text-[11px] text-slate-300">
                  <span>EXPIRES: 12/28</span>
                  <span>CVC: •••</span>
                </div>
              </div>

              <Button
                onClick={handleProcessPayment}
                disabled={processing}
                className="w-full h-11 text-xs font-bold gap-2 shadow"
              >
                {processing ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" /> Processing Payment...
                  </>
                ) : (
                  <>
                    <DollarSign className="h-4 w-4" /> Pay ${booking.amount} Now
                  </>
                )}
              </Button>
            </div>
          )}
        </CardContent>

        <CardFooter className="border-t bg-slate-50/50 p-4 text-center justify-center text-[11px] text-muted-foreground">
          Safe 256-bit SSL Encrypted Simulated Transaction
        </CardFooter>
      </Card>
    </div>
  );
};
