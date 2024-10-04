import { ResponsiveLine } from "@nivo/line";
import { useTheme, useMediaQuery } from "@mui/material";
import { tokens } from "../theme";

const LineChart = ({
  data,
  isCustomLineColors = false,
  isDashboard = false,
}) => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));

  // Function to format tick values
  const formatTick = (year) => {
    return parseInt(year) % 5 === 0 ? year : "";
  };

  return (
    <ResponsiveLine
      data={data}
      theme={{
        axis: {
          domain: {
            line: {
              stroke: colors.grey[100],
            },
          },
          legend: {
            text: {
              fill: "black",
            },
          },
          ticks: {
            line: {
              stroke: colors.grey[100],
              strokeWidth: 1,
            },
            text: {
              fill: "black",
            },
          },
        },
        legends: {
          text: {
            fill: "black",
          },
        },
        tooltip: {
          container: {
            color: "black", // Set the tooltip text color to black
            background: "#fff",
          },
        },
      }}
      colors={isDashboard ? { datum: "color" } : { scheme: "nivo" }}
      margin={{ top: 50, right: 20, bottom: 50, left: 45 }}
      xScale={{ type: "point" }}
      yScale={{
        type: "linear",
        min: "auto",
        max: "auto",
        stacked: true,
        reverse: false,
      }}
      yFormat=" >-1"
      curve="catmullRom"
      axisTop={null}
      axisRight={null}
      axisBottom={{
        orient: "bottom",
        tickSize: 5,
        tickPadding: 5,
        tickRotation: 0,
        legend: "Year", // Already specified as 'Year'
        legendOffset: 36,
        legendPosition: "middle",
        tickValues: data[0]?.data.map((d) => d.x),
        format: (d) => formatTick(d), // Apply the format function here
      }}
      axisLeft={{
        orient: "left",
        tickValues: 5,
        tickSize: 3,
        tickPadding: 5,
        tickRotation: 0,
        legend: "Frequency", // Changed from 'count' to 'Frequency'
        legendOffset: -40,
        legendPosition: "middle",
      }}
      enableGridX={false}
      enableGridY={false}
      pointSize={8}
      pointColor={{ theme: "background" }}
      pointBorderWidth={2}
      pointBorderColor={{ from: "serieColor" }}
      pointLabelYOffset={-12}
      useMesh={true}
      tooltip={({ point }) => (
        <div
          style={{
            background: "white",
            padding: "8px 10px",
            border: "1px solid #ccc",
            color: "black", // Set the text color to black
            fontSize: "12px", // Set a smaller font size
          }}
        >
          <strong>Year: {point.data.xFormatted}</strong>
          <br />
          <strong>Frequency: {point.data.yFormatted}</strong>
        </div>
      )}
      legends={[
        {
          anchor: "top-right",
          direction: "column",
          justify: false,
          translateX: 20,
          translateY: 0,
          itemsSpacing: 0,
          itemDirection: "left-to-right",
          itemWidth: 80,
          itemHeight: 20,
          itemOpacity: 0.75,
          symbolSize: 12,
          symbolShape: "circle",
          symbolBorderColor: "rgba(0, 0, 0, .5)",
          effects: [
            {
              on: "hover",
              style: {
                itemBackground: "rgba(0, 0, 0, .03)",
                itemOpacity: 1,
              },
            },
          ],
        },
      ]}
    />
  );
};

export default LineChart;
