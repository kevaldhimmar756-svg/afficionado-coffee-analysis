import streamlit as st
import pandas as pd
import plotly.express as px

# Page config
st.set_page_config(
    page_title="Afficionado Coffee Roasters",
    page_icon="☕",
    layout="wide"
)

# Load data
@st.cache_data
def load_data():
    df = pd.read_excel(r"C:\Users\HP\Downloads\Afficionado Coffee Roasters.xlsx")
    df['transaction_time'] = pd.to_datetime(df['transaction_time'], format='%H:%M:%S')
    df['hour'] = df['transaction_time'].dt.hour
    df['day_of_week'] = pd.to_datetime('2025-01-01').day_name()
    df['revenue'] = df['transaction_qty'] * df['unit_price']
    return df

df = load_data()

# Title
st.title("☕ Afficionado Coffee Roasters")
st.subheader("Sales Trend & Time-Based Performance Analysis")
st.markdown("---")

# Quick KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Transactions", f"{len(df):,}")
col2.metric("Total Revenue", f"${df['revenue'].sum():,.0f}")
col3.metric("Avg Transaction Value", f"${df['revenue'].mean():.2f}")
col4.metric("Total Stores", f"{df['store_location'].nunique()}")

st.markdown("---")

# Sidebar filters
st.sidebar.header("🔍 Filters")
locations = ["All"] + sorted(df['store_location'].unique().tolist())
selected_location = st.sidebar.selectbox("Store Location", locations)

hour_range = st.sidebar.slider("Hour Range", 0, 23, (6, 21))

metric = st.sidebar.radio("Show by", ["Revenue", "Quantity"])
metric_col = "revenue" if metric == "Revenue" else "transaction_qty"

# Apply filters
filtered_df = df.copy()
if selected_location != "All":
    filtered_df = filtered_df[filtered_df['store_location'] == selected_location]
filtered_df = filtered_df[
    (filtered_df['hour'] >= hour_range[0]) & 
    (filtered_df['hour'] <= hour_range[1])
]

st.subheader(f"Showing {len(filtered_df):,} transactions")

st.markdown("---")

# Chart 1: Revenue by Hour
st.subheader("⏰ Hourly Demand Analysis")
hourly = filtered_df.groupby('hour')[metric_col].sum().reset_index()
fig1 = px.bar(hourly, x='hour', y=metric_col,
              title=f"{metric} by Hour of Day",
              labels={'hour': 'Hour (24hr)', metric_col: metric},
              color=metric_col, color_continuous_scale='reds')
st.plotly_chart(fig1, use_container_width=True)

st.markdown("---")

# Chart 2: Time Bucket Analysis
st.subheader("🕐 Time Period Performance")

def get_time_bucket(hour):
    if 6 <= hour <= 11:
        return "Morning (6-11)"
    elif 12 <= hour <= 16:
        return "Afternoon (12-16)"
    elif 17 <= hour <= 21:
        return "Evening (17-21)"
    else:
        return "Late Hours (22-5)"

filtered_df = filtered_df.copy()
filtered_df['time_bucket'] = filtered_df['hour'].apply(get_time_bucket)

bucket_order = ["Morning (6-11)", "Afternoon (12-16)", 
                "Evening (17-21)", "Late Hours (22-5)"]
bucket = filtered_df.groupby('time_bucket')[metric_col].sum().reset_index()
bucket['time_bucket'] = pd.Categorical(bucket['time_bucket'], 
                        categories=bucket_order, ordered=True)
bucket = bucket.sort_values('time_bucket')

fig2 = px.bar(bucket, x='time_bucket', y=metric_col,
              title=f"{metric} by Time Period",
              labels={'time_bucket': 'Time Period', metric_col: metric},
              color='time_bucket')
st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# Chart 3: Revenue by Store Location
st.subheader("📍 Store Location Comparison")
store = filtered_df.groupby('store_location')[metric_col].sum().reset_index()
fig3 = px.bar(store, x='store_location', y=metric_col,
              title=f"{metric} by Store Location",
              labels={'store_location': 'Location', metric_col: metric},
              color='store_location')
st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# Chart 4: Heatmap - Hour vs Store Location
st.subheader("🌡️ Hourly Heatmap by Store Location")
heatmap_data = filtered_df.groupby(['store_location', 'hour'])[metric_col].sum().reset_index()
heatmap_pivot = heatmap_data.pivot(index='store_location', columns='hour', values=metric_col)
fig4 = px.imshow(heatmap_pivot,
                 title=f"{metric} Heatmap: Store vs Hour",
                 labels=dict(x="Hour of Day", y="Store Location", color=metric),
                 color_continuous_scale='reds',
                 aspect='auto')
st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

# Chart 5: Revenue by Product Category
st.subheader("☕ Product Category Performance")
category = filtered_df.groupby('product_category')[metric_col].sum().reset_index()
category = category.sort_values(metric_col, ascending=False)
fig5 = px.bar(category, x='product_category', y=metric_col,
              title=f"{metric} by Product Category",
              labels={'product_category': 'Category', metric_col: metric},
              color=metric_col, color_continuous_scale='reds')
st.plotly_chart(fig5, use_container_width=True)

st.markdown("---")

# Chart 6: Top 10 Products
st.subheader("🏆 Top 10 Best Selling Products")
top_products = filtered_df.groupby('product_type')[metric_col].sum().reset_index()
top_products = top_products.sort_values(metric_col, ascending=False).head(10)
fig6 = px.bar(top_products, x=metric_col, y='product_type',
              orientation='h',
              title=f"Top 10 Products by {metric}",
              labels={'product_type': 'Product', metric_col: metric},
              color=metric_col, color_continuous_scale='blues')
st.plotly_chart(fig6, use_container_width=True)

st.markdown("---")
st.caption("Dashboard built by Keval Dhimmar | Data Source: Afficionado Coffee Roasters | Tools: Python, Streamlit, Plotly")