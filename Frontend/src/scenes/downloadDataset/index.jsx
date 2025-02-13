import React, { useState } from "react";
import { Box, Button, TextField, Typography } from "@mui/material";
import DownloadOutlinedIcon from "@mui/icons-material/DownloadOutlined";
import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { saveAs } from "file-saver";

const DownloadDataset = () => {
  const [fromDate, setFromDate] = useState("");
  const [toDate, setToDate] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const downloadCSV = async () => {
    if (!fromDate || !toDate) {
      toast.error("Please select both 'From' and 'To' dates.");
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch(
        "https://mdp.vishvasnews.com/api/fetchAllData",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ from: fromDate, to: toDate }),
        }
      );

      if (!response.ok) {
        let errorMessage = "Failed to fetch data.";
        try {
          const errorResponse = await response.json();
          errorMessage = errorResponse.error || errorMessage;
        } catch (jsonError) {
          console.error("Error parsing JSON response:", jsonError);
        }

        if (response.status === 400) {
          errorMessage =
            "Invalid request. Please ensure both dates are correctly selected.";
        } else if (response.status === 404) {
          errorMessage = "No stories found within the selected date range.";
        } else if (response.status === 500) {
          errorMessage = "Server error. Please try again later.";
        }

        toast.error(errorMessage);
        throw new Error(errorMessage);
      }

      const blob = await response.blob();
      const filename = `filteredData_${fromDate}_to_${toDate}.csv`;

      saveAs(blob, filename);
      toast.success("Dataset downloaded successfully!");
    } catch (error) {
      console.error("Error downloading CSV:", error);
      toast.error(error.message || "Error downloading CSV.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Box display="flex" justifyContent="center" gap={2} mt={2}>
      <TextField
        type="date"
        label="From Date"
        InputLabelProps={{ shrink: true, style: { color: "black" } }}
        InputProps={{ style: { color: "black" } }}
        sx={{
          width: "200px",
          "& .MuiOutlinedInput-root": {
            "& fieldset": { borderColor: "black" },
            "&:hover fieldset": { borderColor: "black" },
            "&.Mui-focused fieldset": { borderColor: "black" },
          },
          "& .MuiInputLabel-root.Mui-focused": { color: "black" },
        }}
        value={fromDate}
        onChange={(e) => setFromDate(e.target.value)}
        disabled={isLoading}
      />

      <TextField
        type="date"
        label="To Date"
        InputLabelProps={{ shrink: true, style: { color: "black" } }}
        InputProps={{ style: { color: "black" } }}
        sx={{
          width: "200px",
          "& .MuiOutlinedInput-root": {
            "& fieldset": { borderColor: "black" },
            "&:hover fieldset": { borderColor: "black" },
            "&.Mui-focused fieldset": { borderColor: "black" },
          },
          "& .MuiInputLabel-root.Mui-focused": { color: "black" },
        }}
        value={toDate}
        onChange={(e) => setToDate(e.target.value)}
        disabled={isLoading}
      />

      <Button
        variant="contained"
        startIcon={<DownloadOutlinedIcon />}
        onClick={downloadCSV}
        sx={{
          backgroundColor: isLoading ? "#999" : "#0b9933",
          color: "white",
          fontSize: "14px",
          fontWeight: "bold",
          padding: "10px 20px",
          borderRadius: "50px",
        }}
        disabled={isLoading}
      >
        {isLoading ? "Downloading..." : "Download Dataset"}
      </Button>
    </Box>
  );
};

export default DownloadDataset;
