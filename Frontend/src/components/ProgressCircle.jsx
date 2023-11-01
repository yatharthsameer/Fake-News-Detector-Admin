import { Box, Typography, useTheme } from "@mui/material";
import { tokens } from "../theme";

const ProgressCircle = ({ progress = 0.75, size = 40 }) => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const percentage = Math.round(progress * 100);

  const angle = progress * 360;

  return (
    <Box
      sx={{
        position: "relative",
        width: `${size}px`,
        height: `${size}px`,
      }}
    >
      <Box
        sx={{
          background: `radial-gradient(${colors.primary[400]} 55%, transparent 56%),
            conic-gradient(transparent 0deg ${angle}deg, ${colors.primary[900]} ${angle}deg 360deg),
            ${colors.greenAccent[500]}`,
          borderRadius: "50%",
          width: `${size}px`,
          height: `${size}px`,
          position: "absolute",
        }}
      />
      <Typography
        variant="body1"
        sx={{
          position: "absolute",
          top: "50%",
          left: "50%",
          transform: "translate(-50%, -50%)",
          color: colors.grey[100], // Adjust the color as needed
          fontSize: "25px", // Adjust the desired font size
        }}
      >
        {`${percentage}%`}
      </Typography>
    </Box>
  );
};

export default ProgressCircle;
