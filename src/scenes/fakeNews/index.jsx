import { Box } from "@mui/material";
import { DataGrid, GridToolbar } from "@mui/x-data-grid";
import { tokens } from "../../theme";
import Header from "../../components/Header";
import { useTheme } from "@mui/material";

const FakeNews = ({ data }) => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);

  const columns = [
    { field: "Story_Date", headerName: "Date", width: 150 },
    {
      field: "Story_URL",
      headerName: "Story URL",
      width: 250,
      renderCell: (params) => (
        <a href={params.value} target="_blank" rel="noopener noreferrer">
          View Story
        </a>
      ),
    },
    { field: "Headline", headerName: "Headline", width: 250 },
    {
      field: "Claim_URL",
      headerName: "Claim URL",
      width: 250,
      renderCell: (params) => (
        <a href={params.value} target="_blank" rel="noopener noreferrer">
          View Claim
        </a>
      ),
    },
    { field: "What_(Claim)", headerName: "Claim", width: 200 },
    {
      field: "img",
      headerName: "Image",
      width: 150,
      renderCell: (params) => (
        <img src={params.value} alt="News Image" width="50" height="50" />
      ),
    },
  ];

  return (
    <Box m="20px">
      <Header title="Fake News" subtitle="List of Fake News" />
      <Box
        m="40px 0 0 0"
        height="75vh"
        sx={
          {
            
          "& .MuiDataGrid-root": {
            border: "none",
          },
          "& .MuiDataGrid-cell": {
            borderBottom: "none",
          },
          "& .name-column--cell": {
            color: colors.greenAccent[300],
          },
          "& .MuiDataGrid-columnHeaders": {
            backgroundColor: colors.blueAccent[700],
            borderBottom: "none",
          },
          "& .MuiDataGrid-virtualScroller": {
            backgroundColor: colors.primary[400],
          },
          "& .MuiDataGrid-footerContainer": {
            borderTop: "none",
            backgroundColor: colors.blueAccent[700],
          },
          "& .MuiCheckbox-root": {
            color: `${colors.greenAccent[200]} !important`,
          },
          "& .MuiDataGrid-toolbarContainer .MuiButton-text": {
            color: `${colors.grey[100]} !important`,
          },
            // ... (your existing styles here)
          }
        }
      >
        <DataGrid
          rows={data}
          columns={columns}
          components={{ Toolbar: GridToolbar }}
        />
      </Box>
    </Box>
  );
};

export default FakeNews;
