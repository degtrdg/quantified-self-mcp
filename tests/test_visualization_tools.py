#!/usr/bin/env python3
"""Test script for visualization tools with mocked inputs and outputs"""

import sys
import os
from unittest.mock import Mock, patch, MagicMock
import base64

# Add the research_agent directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'research_agent'))

def test_create_visualization():
    """Test create_visualization function with mocked matplotlib"""
    print("🔍 Testing create_visualization...")
    
    # Mock data for visualization
    mock_data = [
        {'date': '2024-01-01', 'exercise': 'deadlift', 'weight': 225, 'mood_rating': 4},
        {'date': '2024-01-02', 'exercise': 'bench press', 'weight': 185, 'mood_rating': 5},
        {'date': '2024-01-03', 'exercise': 'squat', 'weight': 205, 'mood_rating': 3},
        {'date': '2024-01-04', 'exercise': 'deadlift', 'weight': 235, 'mood_rating': 5},
        {'date': '2024-01-05', 'exercise': 'bench press', 'weight': 190, 'mood_rating': 4}
    ]
    
    with patch('research_agent.tools.visualization.plt') as mock_plt, \
         patch('research_agent.tools.visualization.pd') as mock_pd, \
         patch('research_agent.tools.visualization.io') as mock_io:
        
        # Mock pandas DataFrame
        mock_df = Mock()
        mock_pd.DataFrame.return_value = mock_df
        mock_df.__getitem__ = Mock(side_effect=lambda x: [1, 2, 3, 4, 5])
        mock_df.sort_values.return_value = mock_df
        mock_pd.to_datetime.return_value = mock_df
        
        # Mock matplotlib
        mock_plt.figure.return_value = Mock()
        mock_plt.plot.return_value = Mock()
        mock_plt.bar.return_value = Mock()
        mock_plt.scatter.return_value = Mock()
        mock_plt.hist.return_value = Mock()
        
        # Mock BytesIO for base64 encoding
        mock_buffer = Mock()
        mock_io.BytesIO.return_value = mock_buffer
        mock_buffer.getvalue.return_value = b'fake_image_data'
        
        from research_agent.tools.visualization import create_visualization
        
        # Test line chart
        result = create_visualization(
            data=mock_data,
            chart_type="line",
            title="Weight Progress Over Time",
            x_column="date",
            y_column="weight"
        )
        
        print("✅ Line chart creation result:")
        print(result)
        print()
        
        # Test bar chart
        result = create_visualization(
            data=mock_data,
            chart_type="bar", 
            title="Exercise Distribution",
            x_column="exercise",
            y_column="weight"
        )
        
        print("✅ Bar chart creation result:")
        print(result)
        print()
        
        # Test scatter plot
        result = create_visualization(
            data=mock_data,
            chart_type="scatter",
            title="Weight vs Mood",
            x_column="weight", 
            y_column="mood_rating"
        )
        
        print("✅ Scatter plot creation result:")
        print(result)
        print()
        
        # Test histogram
        result = create_visualization(
            data=mock_data,
            chart_type="histogram",
            title="Weight Distribution",
            y_column="weight"
        )
        
        print("✅ Histogram creation result:")
        print(result)
        print()

def test_create_time_series():
    """Test create_time_series function"""
    print("🔍 Testing create_time_series...")
    
    # Mock time series data
    mock_time_data = [
        {'date': '2024-01-01', 'avg_heart_rate': 145},
        {'date': '2024-01-02', 'avg_heart_rate': 152},
        {'date': '2024-01-03', 'avg_heart_rate': 138},
        {'date': '2024-01-04', 'avg_heart_rate': 160},
        {'date': '2024-01-05', 'avg_heart_rate': 148},
        {'date': '2024-01-06', 'avg_heart_rate': 155},
        {'date': '2024-01-07', 'avg_heart_rate': 142}
    ]
    
    with patch('research_agent.tools.visualization.plt') as mock_plt, \
         patch('research_agent.tools.visualization.pd') as mock_pd, \
         patch('research_agent.tools.visualization.mdates') as mock_mdates, \
         patch('research_agent.tools.visualization.io') as mock_io:
        
        # Mock pandas DataFrame
        mock_df = Mock()
        mock_pd.DataFrame.return_value = mock_df
        mock_pd.to_datetime.return_value = [1, 2, 3, 4, 5, 6, 7]
        mock_df.__getitem__ = Mock(side_effect=lambda x: [1, 2, 3, 4, 5, 6, 7])
        mock_df.sort_values.return_value = mock_df
        
        # Mock matplotlib and dates
        mock_plt.figure.return_value = Mock()
        mock_plt.plot.return_value = Mock()
        mock_plt.gca.return_value = Mock()
        mock_mdates.DateFormatter.return_value = Mock()
        mock_mdates.DayLocator.return_value = Mock()
        
        # Mock BytesIO
        mock_buffer = Mock()
        mock_io.BytesIO.return_value = mock_buffer
        mock_buffer.getvalue.return_value = b'fake_timeseries_data'
        
        from research_agent.tools.visualization import create_time_series
        
        result = create_time_series(
            data=mock_time_data,
            date_column="date",
            value_column="avg_heart_rate",
            title="Heart Rate Over Time"
        )
        
        print("✅ Time series creation result:")
        print(result)
        print()

def test_create_correlation_matrix():
    """Test create_correlation_matrix function"""
    print("🔍 Testing create_correlation_matrix...")
    
    # Mock correlation data
    mock_corr_data = [
        {'weight': 225, 'heart_rate': 145, 'mood_rating': 4, 'sleep_hours': 7.5},
        {'weight': 185, 'heart_rate': 152, 'mood_rating': 5, 'sleep_hours': 8.0},
        {'weight': 205, 'heart_rate': 138, 'mood_rating': 3, 'sleep_hours': 6.5},
        {'weight': 235, 'heart_rate': 160, 'mood_rating': 5, 'sleep_hours': 8.5},
        {'weight': 190, 'heart_rate': 148, 'mood_rating': 4, 'sleep_hours': 7.0}
    ]
    
    with patch('research_agent.tools.visualization.plt') as mock_plt, \
         patch('research_agent.tools.visualization.pd') as mock_pd, \
         patch('research_agent.tools.visualization.np') as mock_np, \
         patch('research_agent.tools.visualization.io') as mock_io:
        
        # Mock pandas DataFrame and correlation matrix
        mock_df = Mock()
        mock_pd.DataFrame.return_value = mock_df
        
        # Mock correlation matrix
        mock_corr_matrix = Mock()
        mock_corr_matrix.columns = ['weight', 'heart_rate', 'mood_rating', 'sleep_hours']
        mock_corr_matrix.index = ['weight', 'heart_rate', 'mood_rating', 'sleep_hours']
        mock_corr_matrix.iloc = Mock()
        mock_corr_matrix.iloc.__getitem__ = Mock(return_value=Mock(__getitem__=Mock(return_value=0.75)))
        
        # Mock select_dtypes and corr
        mock_numeric_data = Mock()
        mock_numeric_data.empty = False
        mock_numeric_data.corr.return_value = mock_corr_matrix
        mock_df.__getitem__.return_value.select_dtypes.return_value = mock_numeric_data
        
        # Mock matplotlib
        mock_plt.figure.return_value = Mock()
        mock_plt.imshow.return_value = Mock()
        mock_plt.colorbar.return_value = Mock()
        
        # Mock numpy
        mock_np.number = float
        
        # Mock BytesIO
        mock_buffer = Mock()
        mock_io.BytesIO.return_value = mock_buffer
        mock_buffer.getvalue.return_value = b'fake_correlation_data'
        
        from research_agent.tools.visualization import create_correlation_matrix
        
        result = create_correlation_matrix(
            data=mock_corr_data,
            numeric_columns=['weight', 'heart_rate', 'mood_rating', 'sleep_hours'],
            title="Fitness Metrics Correlation Matrix"
        )
        
        print("✅ Correlation matrix creation result:")
        print(result)
        print()

def test_visualization_error_handling():
    """Test error handling scenarios for visualization tools"""
    print("🔍 Testing visualization error handling...")
    
    from research_agent.tools.visualization import create_visualization, create_time_series, create_correlation_matrix
    
    # Test empty data
    result = create_visualization([], "line", "Test", "x", "y")
    print("✅ Empty data handling:")
    print(result)
    print()
    
    # Test missing required parameters
    result = create_visualization([{'x': 1, 'y': 2}], "line", "Test")
    print("✅ Missing parameters handling:")
    print(result)
    print()
    
    # Test unsupported chart type
    result = create_visualization([{'x': 1, 'y': 2}], "pie", "Test", "x", "y")
    print("✅ Unsupported chart type handling:")
    print(result)
    print()
    
    # Test time series with empty data
    result = create_time_series([], "date", "value")
    print("✅ Time series empty data handling:")
    print(result)
    print()
    
    # Test correlation matrix with empty data
    result = create_correlation_matrix([], ["col1", "col2"])
    print("✅ Correlation matrix empty data handling:")
    print(result)
    print()

def test_visualization_with_save_path():
    """Test saving visualizations to file"""
    print("🔍 Testing visualization file saving...")
    
    mock_data = [{'x': 1, 'y': 2}, {'x': 2, 'y': 4}]
    
    with patch('research_agent.tools.visualization.plt') as mock_plt, \
         patch('research_agent.tools.visualization.pd') as mock_pd:
        
        # Mock pandas DataFrame
        mock_df = Mock()
        mock_pd.DataFrame.return_value = mock_df
        mock_df.__getitem__ = Mock(side_effect=lambda x: [1, 2])
        
        # Mock matplotlib
        mock_plt.figure.return_value = Mock()
        mock_plt.plot.return_value = Mock()
        mock_plt.savefig.return_value = Mock()
        
        from research_agent.tools.visualization import create_visualization
        
        result = create_visualization(
            data=mock_data,
            chart_type="line",
            title="Test Chart",
            x_column="x",
            y_column="y",
            save_path="/tmp/test_chart.png"
        )
        
        print("✅ File save result:")
        print(result)
        print()

def main():
    """Run all visualization tool tests"""
    print("🧪 Testing Visualization Tools")
    print("=" * 50)
    
    test_create_visualization()
    test_create_time_series()
    test_create_correlation_matrix()
    test_visualization_error_handling()
    test_visualization_with_save_path()
    
    print("✅ All visualization tool tests completed!")

if __name__ == "__main__":
    main()