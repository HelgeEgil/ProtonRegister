USE [testregister]
GO
/****** Object:  Table [dbo].[DVH]    Script Date: 20.12.2022 10:54:01 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[DVH](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[RTImageSeriesID] [int] NOT NULL,
	[StructureName] [nvarchar](50) NULL,
	[DVH_dose_Gy] [text] NULL,
	[DVH_volume_percent] [text] NULL,
	[StructureVolume_cc] [float] NULL,
 CONSTRAINT [PK_DVH] PRIMARY KEY CLUSTERED 
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[RTImageSeries]    Script Date: 20.12.2022 10:54:01 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[RTImageSeries](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[StudyID] [int] NULL,
	[Modality] [nchar](100) NULL,
	[SeriesInstanceUID] [nchar](100) NULL,
	[SliceThickness_mm] [float] NULL,
	[Manufacturer] [nchar](100) NULL,
	[ManufacturersModelName] [nchar](100) NULL,
	[SeriesTime] [datetime] NULL,
	[kVp] [int] NULL,
	[mAs] [float] NULL,
	[NumberOfStructures] [int] NULL,
	[PrescriptionDose_Gy] [float] NULL,
	[PatientName] [nvarchar](100) NULL,
 CONSTRAINT [PK_RTImageSeries] PRIMARY KEY CLUSTERED 
(
	[ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
