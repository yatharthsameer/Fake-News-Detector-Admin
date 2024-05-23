import React, { useState, useEffect } from "react";
import {
  Box,
  Button,
  Typography,
  CircularProgress,
  ButtonBase,
  useTheme,
} from "@mui/material";
import { tokens } from "../../theme";

const Trendspage = () => {
  const [resultsColumn1, setResultsColumn1] = useState([]);
  const [resultsColumn2, setResultsColumn2] = useState([]);
  const [isLoadingColumn1, setIsLoadingColumn1] = useState(false);
  const [isLoadingColumn2, setIsLoadingColumn2] = useState(false);
  const [currentPageColumn1, setCurrentPageColumn1] = useState(1);
  const [currentPageColumn2, setCurrentPageColumn2] = useState(1);
  const itemsPerPage = 5;

  const indexOfLastItemColumn1 = currentPageColumn1 * itemsPerPage;
  const indexOfFirstItemColumn1 = indexOfLastItemColumn1 - itemsPerPage;
  const currentItemsColumn1 = resultsColumn1.slice(
    indexOfFirstItemColumn1,
    indexOfLastItemColumn1
  );

  const indexOfLastItemColumn2 = currentPageColumn2 * itemsPerPage;
  const indexOfFirstItemColumn2 = indexOfLastItemColumn2 - itemsPerPage;
  const currentItemsColumn2 = resultsColumn2.slice(
    indexOfFirstItemColumn2,
    indexOfLastItemColumn2
  );

  const handleNextColumn1 = () => {
    setCurrentPageColumn1(currentPageColumn1 + 1);
  };

  const handlePrevColumn1 = () => {
    setCurrentPageColumn1(currentPageColumn1 - 1);
  };

  const handleNextColumn2 = () => {
    setCurrentPageColumn2(currentPageColumn2 + 1);
  };

  const handlePrevColumn2 = () => {
    setCurrentPageColumn2(currentPageColumn2 - 1);
  };

  const theme = useTheme();
  const colors = tokens(theme.palette.mode);

  useEffect(() => {
    fetchResultsForColumn1();
    fetchResultsForColumn2();
  }, []);

  const fetchResultsForColumn1 = () => {
    setIsLoadingColumn1(true);
    fetch("/api/ensemble", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        charset: "utf-8",
      },
      body: JSON.stringify({ query: "virat kohli" }),
    })
      .then((response) => response.json())
      .then((data) => {
        setResultsColumn1(data);
        setIsLoadingColumn1(false);
      })
      .catch((error) => {
        console.error("Error fetching data for column 1:", error);
        setIsLoadingColumn1(false);
      });
  };

  const fetchResultsForColumn2 = () => {
    setIsLoadingColumn2(true);

    const currentDate = new Date();
    const formattedDate = `${currentDate.getDate()} ${currentDate.toLocaleString(
      "default",
      { month: "short" }
    )} ${currentDate.getFullYear()}`;
    try {
      // fetch("http://localhost:8080/api/stories-by-date", {
      fetch("/api/stories-by-date", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          charset: "utf-8",
        },
        body: JSON.stringify({ date: formattedDate }),
      })
        .then((response) => response.json())
        .then((data) => {
          console.log(formattedDate);
          setResultsColumn2(data);
          setIsLoadingColumn2(false);
        })

        .catch((error) => {
          console.error("Error fetching data for column 2:", error);
          setIsLoadingColumn2(false);
        });
    } catch (e) {
      console.log(e);
      setIsLoadingColumn2(false);
    }
  };
  const renderResults = (results, currentPage, handlePrev, handleNext) => {
    const indexOfLastItem = currentPage * itemsPerPage;
    const indexOfFirstItem = indexOfLastItem - itemsPerPage;
    const currentItems = results.slice(indexOfFirstItem, indexOfLastItem);

    return (
      <>
        {currentItems.map((result, index) => (
          <Box
            key={index}
            display="flex"
            flexDirection="row"
            alignItems="flex-start"
            borderBottom={`1px solid ${colors.primary[400]}`}
            p="10px 0"
          >
            <ButtonBase
              onClick={() => window.open(result.data.Story_URL, "_blank")}
              sx={{
                marginRight: "20px",
                borderRadius: "4px",
                overflow: "hidden",
              }}
            >
              <img
                src={result.data.img}
                alt="News"
                width="110px"
                height="95px"
                style={{ marginRight: "20px" }}
              />
            </ButtonBase>
            <div>
              <Typography
                color={colors.greenAccent[100]}
                variant="h5"
                fontWeight="600"
              >
                <a
                  href={result.data.Story_URL}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{
                    color: colors.greenAccent[100],
                    textDecoration: "none",
                  }}
                >
                  {result.data.Headline}
                </a>
              </Typography>
              <Typography color={colors.grey[100]}>
                {result.data.Story_Date}
              </Typography>
            </div>
          </Box>
        ))}
        <Box display="flex" justifyContent="center" mt="20px">
          <Button
            onClick={handlePrev}
            disabled={currentPage === 1}
            variant="contained"
            sx={{ mr: 1 }}
          >
            Prev
          </Button>
          <Button
            onClick={handleNext}
            disabled={currentPage === Math.ceil(results.length / itemsPerPage)}
            variant="contained"
            sx={{ ml: 1 }}
          >
            Next
          </Button>
        </Box>
      </>
    );
  };

  return (
    <Box m="20px">
      <Box display="flex" justifyContent="space-between" alignItems="center">
        <Typography variant="h2" color={colors.grey[100]}>
          Trendspage
        </Typography>
      </Box>
      <Box display="flex" justifyContent="space-between" gap="20px" mt="20px">
        <Box flex={1} backgroundColor={colors.primary[400]} p="20px">
          <Typography variant="h5" color={colors.grey[100]} mb="10px">
            Based on current trends
          </Typography>
          {isLoadingColumn1 ? (
            <Box
              display="flex"
              justifyContent="center"
              alignItems="center"
              height="50vh"
            >
              <CircularProgress sx={{ color: colors.blueAccent[600] }} />
              <Typography variant="h6" sx={{ mt: 2 }}>
                Loading...
              </Typography>
            </Box>
          ) : (
            renderResults(
              resultsColumn1,
              currentPageColumn1,
              handlePrevColumn1,
              handleNextColumn1
            )
          )}
        </Box>
        <Box flex={1} backgroundColor={colors.primary[400]} p="20px">
          <Typography variant="h5" color={colors.grey[100]} mb="10px">
            Based on historical trends
          </Typography>
          {isLoadingColumn2 ? (
            <Box
              display="flex"
              justifyContent="center"
              alignItems="center"
              height="50vh"
            >
              <CircularProgress sx={{ color: colors.blueAccent[600] }} />
              <Typography variant="h6" sx={{ mt: 2 }}>
                Loading...
              </Typography>
            </Box>
          ) : (
            renderResults(
              resultsColumn2,
              currentPageColumn2,
              handlePrevColumn2,
              handleNextColumn2
            )
          )}
        </Box>
      </Box>
    </Box>
  );
};

export default Trendspage;
