import { useState } from "react";

interface DateRangePickerProps {
  onDateRangeChange: (fromDate: string, toDate: string) => void;
}

export default function DateRangePicker({ onDateRangeChange }: DateRangePickerProps) {
  const [fromDate, setFromDate] = useState<string>(() => {
    const date = new Date();
    date.setDate(date.getDate() - 7);
    return date.toISOString().split('T')[0];
  });
  
  const [toDate, setToDate] = useState<string>(() => {
    const date = new Date();
    return date.toISOString().split('T')[0];
  });
  
  const toISODateTime = (dateString: string, isEnd = false) => {
    const date = new Date(dateString);
    if (isEnd) {
      date.setHours(23, 59, 59, 999);
    } else {
      date.setHours(0, 0, 0, 0);
    }
    return date.toISOString();
  };
  
  const handleApply = () => {
    onDateRangeChange(
      toISODateTime(fromDate), 
      toISODateTime(toDate, true)
    );
  };
  
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-4 mb-6">
      <h2 className="text-lg font-medium mb-4">Выберите временной диапазон</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <div>
          <label htmlFor="from-date" className="block text-sm font-medium mb-1">
            С даты
          </label>
          <input
            id="from-date"
            type="date"
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            value={fromDate}
            onChange={(e) => setFromDate(e.target.value)}
            max={toDate}
          />
        </div>
        
        <div>
          <label htmlFor="to-date" className="block text-sm font-medium mb-1">
            По дату
          </label>
          <input
            id="to-date"
            type="date"
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            value={toDate}
            onChange={(e) => setToDate(e.target.value)}
            min={fromDate}
            max={new Date().toISOString().split('T')[0]}
          />
        </div>
      </div>
      
      <div className="flex justify-end">
        <button
          type="button"
          onClick={handleApply}
          className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 border border-transparent rounded-md hover:bg-indigo-700 focus:outline-none"
        >
          Применить диапазон
        </button>
      </div>
    </div>
  );
}
