import React, { useMemo } from 'react';
import { Box, Card, CardContent, IconButton, Typography, Chip } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';
import ImageIcon from '@mui/icons-material/Image';
import InsertDriveFileIcon from '@mui/icons-material/InsertDriveFile';

interface FilePreviewProps {
  files: File[];
  onRemove: (index: number) => void;
}

const getFileIcon = (file: File) => {
  const extension = file.name.split('.').pop()?.toLowerCase();
  
  if (extension === 'pdf') {
    return <PictureAsPdfIcon sx={{ fontSize: 48, color: 'error.main' }} />;
  }
  
  if (['jpg', 'jpeg', 'png'].includes(extension || '')) {
    return <ImageIcon sx={{ fontSize: 48, color: 'primary.main' }} />;
  }
  
  if (['dcm', 'dicom'].includes(extension || '')) {
    return <InsertDriveFileIcon sx={{ fontSize: 48, color: 'info.main' }} />;
  }
  
  return <InsertDriveFileIcon sx={{ fontSize: 48, color: 'grey.500' }} />;
};

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
};

const FilePreviewCard: React.FC<{ file: File; index: number; onRemove: (index: number) => void }> = ({
  file,
  index,
  onRemove,
}) => {
  const thumbnailUrl = useMemo(() => {
    const extension = file.name.split('.').pop()?.toLowerCase();
    
    // Only create object URL for image files
    if (['jpg', 'jpeg', 'png'].includes(extension || '')) {
      return URL.createObjectURL(file);
    }
    
    return null;
  }, [file]);

  // Cleanup object URL when component unmounts
  React.useEffect(() => {
    return () => {
      if (thumbnailUrl) {
        URL.revokeObjectURL(thumbnailUrl);
      }
    };
  }, [thumbnailUrl]);

  return (
    <Card
      sx={{
        position: 'relative',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      <IconButton
        size="small"
        onClick={() => onRemove(index)}
        sx={{
          position: 'absolute',
          top: 8,
          right: 8,
          backgroundColor: 'background.paper',
          '&:hover': {
            backgroundColor: 'error.light',
            color: 'error.contrastText',
          },
          zIndex: 1,
        }}
        aria-label={`Remove ${file.name}`}
      >
        <DeleteIcon fontSize="small" />
      </IconButton>

      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          height: 120,
          backgroundColor: 'grey.100',
          overflow: 'hidden',
        }}
      >
        {thumbnailUrl ? (
          <img
            src={thumbnailUrl}
            alt={file.name}
            style={{
              maxWidth: '100%',
              maxHeight: '100%',
              objectFit: 'contain',
            }}
          />
        ) : (
          getFileIcon(file)
        )}
      </Box>

      <CardContent sx={{ flexGrow: 1, pt: 2 }}>
        <Typography
          variant="body2"
          noWrap
          title={file.name}
          sx={{ fontWeight: 500, mb: 1 }}
        >
          {file.name}
        </Typography>
        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          <Chip
            label={formatFileSize(file.size)}
            size="small"
            variant="outlined"
          />
          <Chip
            label={file.name.split('.').pop()?.toUpperCase()}
            size="small"
            color="primary"
            variant="outlined"
          />
        </Box>
      </CardContent>
    </Card>
  );
};

export const FilePreview: React.FC<FilePreviewProps> = ({ files, onRemove }) => {
  if (files.length === 0) {
    return null;
  }

  return (
    <Box sx={{ mt: 3 }}>
      <Typography variant="h6" gutterBottom>
        Selected Files ({files.length})
      </Typography>
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: {
            xs: '1fr',
            sm: 'repeat(2, 1fr)',
            md: 'repeat(3, 1fr)',
            lg: 'repeat(4, 1fr)',
          },
          gap: 2,
        }}
      >
        {files.map((file, index) => (
          <FilePreviewCard
            key={`${file.name}-${index}`}
            file={file}
            index={index}
            onRemove={onRemove}
          />
        ))}
      </Box>
    </Box>
  );
};
