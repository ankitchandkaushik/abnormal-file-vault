import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { fileService } from '../services/fileService';

export const StorageSavings: React.FC = () => {
  const { data: savings, isLoading } = useQuery({
    queryKey: ['storage_savings'],
    queryFn: fileService.getStorageSavings,
  });

  if (isLoading) {
    return (
      <div className="mb-6 text-gray-500">Loading storage savings...</div>
    );
  }

  if (!savings) return null;

  return (
    <div className="mb-6 bg-green-50 border-l-4 border-green-400 p-4 rounded">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <span className="font-semibold text-green-700">Storage Savings:</span>
          <span className="ml-2 text-green-700">
            {((savings.savings || 0) / 1024).toFixed(2)} KB saved
          </span>
        </div>
        <div className="mt-2 sm:mt-0 text-xs text-gray-600">
          Total files: {savings.total_files} | Unique files: {savings.unique_files} | 
          Total size: {((savings.total_size || 0) / 1024).toFixed(2)} KB | 
          Unique size: {((savings.unique_size || 0) / 1024).toFixed(2)} KB
        </div>
      </div>
    </div>
  );
};