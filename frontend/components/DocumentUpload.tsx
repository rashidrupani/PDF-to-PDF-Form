import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Box, Typography, Paper, Alert } from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import { styled } from '@mui/material/styles';

const StyledDropzone = styled(Paper)(({ theme }) => ({
  border: `2px dashed ${theme.palette.divider}`,
  borderRadius: theme.spacing(1),
  padding: theme.spacing(4),
  textAlign: 'center',
  cursor: 'pointer',
  transition: 'border-color 0.2s ease-in-out',
  '&:hover': {
    borderColor: theme.palette.primary.main,
  },
  '&.active': {
    borderColor: theme.palette.primary.main,
    backgroundColor: theme.palette.action.hover,
  },
}));

interface DocumentUploadProps {
  onFilesUploaded: (files: File[]) => void;
}

export default function DocumentUpload({ onFilesUploaded }: DocumentUploadProps) {
  const onDrop = useCallback((acceptedFiles: File[]) => {
    onFilesUploaded(acceptedFiles);
  }, [onFilesUploaded]);

  const { getRootProps, getInputProps, isDragActive, acceptedFiles } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
      'image/tiff': ['.tiff', '.tif'],
    },
    multiple: false, // Only allow single file for simplicity
  });

  return (
    <Box>
      <StyledDropzone
        {...getRootProps()}
        className={isDragActive ? 'active' : ''}
      >
        <input {...getInputProps()} />
        <CloudUploadIcon sx={{ fontSize: 60, color: 'action.active', mb: 2 }} />
        <Typography variant="h6" gutterBottom>
          {isDragActive ? 'Drop the file here' : 'Drag & drop a file here, or click to select'}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Supports PDF, JPG, PNG, TIFF formats. Max file size: 50MB.
        </Typography>
      </StyledDropzone>

      {acceptedFiles.length > 0 && (
        <Box mt={2}>
          <Alert severity="info">
            {acceptedFiles.length} file(s) selected for processing
          </Alert>
          <Box mt={1}>
            {acceptedFiles.map((file, index) => (
              <Typography key={index} variant="body2" color="text.secondary">
                {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)
              </Typography>
            ))}
          </Box>
        </Box>
      )}
    </Box>
  );
}