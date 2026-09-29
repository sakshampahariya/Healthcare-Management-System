import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { CalendarCheck, Eye, CreditCard, XCircle } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { bookingsApi, Booking } from "@/services/api";

export const MyBookings: React.FC = () => {
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [loading, setLoading] = useState(true);

  const fetchBookings = async () => {
    setLoading(true);
    try {
      const res = await bookingsApi.list(1, 100);
      if (res.success && res.data) {
        setBookings(res.data);
      }
    } catch (err) {
      console.error("Failed to load bookings:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBookings();
  }, []);

  const handleCancelBooking = async (id: number) => {
    if (!window.confirm("Are you sure you want to cancel this booking?")) return;

    try {
      const res = await bookingsApi.cancel(id);
      if (res.success) {
        fetchBookings();
      }
    } catch (err: any) {
      alert(err.response?.data?.error?.message || "Failed to cancel booking");
    }
  };

  const filteredBookings = bookings.filter((b) => {
    if (statusFilter === "ALL") return true;
    return b.status === statusFilter;
  });

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "CONFIRMED":
        return <Badge variant="success">Confirmed</Badge>;
      case "PENDING":
        return <Badge variant="warning">Pending Payment</Badge>;
      case "CANCELLED":
        return <Badge variant="destructive">Cancelled</Badge>;
      case "FAILED":
        return <Badge variant="destructive">Payment Failed</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b pb-5">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">My Bookings</h2>
          <p className="text-xs text-muted-foreground mt-1">
            Track your appointment status, manage payments, or view booking details.
          </p>
        </div>
        <Link to="/tests">
          <Button size="sm" className="gap-2 text-xs font-semibold">
            <CalendarCheck className="h-4 w-4" /> Book New Test
          </Button>
        </Link>
      </div>

      {/* Status Filter Tabs */}
      <div className="flex items-center justify-between">
        <Tabs value={statusFilter} onValueChange={setStatusFilter} className="w-auto">
          <TabsList>
            <TabsTrigger value="ALL" className="text-xs">
              All ({bookings.length})
            </TabsTrigger>
            <TabsTrigger value="PENDING" className="text-xs">
              Pending ({bookings.filter((b) => b.status === "PENDING").length})
            </TabsTrigger>
            <TabsTrigger value="CONFIRMED" className="text-xs">
              Confirmed ({bookings.filter((b) => b.status === "CONFIRMED").length})
            </TabsTrigger>
            <TabsTrigger value="CANCELLED" className="text-xs">
              Cancelled ({bookings.filter((b) => b.status === "CANCELLED").length})
            </TabsTrigger>
          </TabsList>
        </Tabs>
      </div>

      {/* Bookings Table */}
      <Card className="shadow-sm">
        <CardHeader className="pb-3">
          <CardTitle className="text-base font-bold">Booking History</CardTitle>
          <CardDescription className="text-xs">
            List of all diagnostic test appointments registered under your account.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="text-xs">Booking ID</TableHead>
                <TableHead className="text-xs">Appointment Datetime</TableHead>
                <TableHead className="text-xs">Test ID</TableHead>
                <TableHead className="text-xs">Centre ID</TableHead>
                <TableHead className="text-xs">Total Amount</TableHead>
                <TableHead className="text-xs">Status</TableHead>
                <TableHead className="text-xs text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={7} className="text-center text-xs py-8 text-muted-foreground">
                    Loading your bookings...
                  </TableCell>
                </TableRow>
              ) : filteredBookings.length > 0 ? (
                filteredBookings.map((booking) => (
                  <TableRow key={booking.id}>
                    <TableCell className="font-bold text-xs">#{booking.id}</TableCell>
                    <TableCell className="text-xs">
                      {new Date(booking.appointment_datetime).toLocaleString(undefined, {
                        dateStyle: "medium",
                        timeStyle: "short",
                      })}
                    </TableCell>
                    <TableCell className="text-xs font-medium">Test #{booking.test_id}</TableCell>
                    <TableCell className="text-xs font-medium">Centre #{booking.centre_id}</TableCell>
                    <TableCell className="font-bold text-xs">${booking.amount}</TableCell>
                    <TableCell>{getStatusBadge(booking.status)}</TableCell>
                    <TableCell className="text-right">
                      <div className="flex items-center justify-end gap-2">
                        <Link to={`/bookings/${booking.id}`}>
                          <Button variant="ghost" size="sm" className="h-8 gap-1 text-xs">
                            <Eye className="h-3.5 w-3.5" /> Details
                          </Button>
                        </Link>
                        {booking.status === "PENDING" && (
                          <>
                            <Link to={`/payment/${booking.id}`}>
                              <Button size="sm" className="h-8 gap-1 text-xs font-semibold">
                                <CreditCard className="h-3.5 w-3.5" /> Pay
                              </Button>
                            </Link>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleCancelBooking(booking.id)}
                              className="h-8 text-xs text-rose-600 hover:bg-rose-50"
                              title="Cancel Booking"
                            >
                              <XCircle className="h-3.5 w-3.5" />
                            </Button>
                          </>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={7} className="text-center text-xs py-10 text-muted-foreground">
                    No bookings match your filter criteria.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
};
