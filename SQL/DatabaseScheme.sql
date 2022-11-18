CREATE SCHEMA [DICOM]
GO

CREATE TABLE [DICOM].[Institution] (
  [ID] int,
  [Name] nvarchar(255),
  [Location] nvarchar(255),
  PRIMARY KEY ([ID])
)
GO

CREATE TABLE [DICOM].[Patient] (
  [ID] int,
  [HelseforetakID] int,
  [name] nvarchar(255),
  [PID] nvarchar(255),
  [PrimaryTumorSite] nvarchar(255),
  PRIMARY KEY ([ID])
)
GO

CREATE TABLE [DICOM].[Study] (
  [ID] int,
  [PatientID] int,
  [StudyInstanceUID] nvarchar(255),
  [StudyTime] datetime,
  PRIMARY KEY ([ID], [PatientID], [StudyInstanceUID])
)
GO

CREATE TABLE [DICOM].[RTImageSeries] (
  [ID] int,
  [StudyID] int,
  [Modality] nvarchar(255),
  [SeriesInstanceUID] nvarchar(255),
  [SliceThickness] float,
  [Manufacturer] nvarchar(255),
  [ManufacturersModelName] nvarchar(255),
  [SeriesTime] datetime,
  [kVp] int,
  [mAs] int,
  PRIMARY KEY ([ID], [StudyID])
)
GO

CREATE TABLE [DICOM].[RTStructSeries] (
  [ID] int,
  [StudyID] int,
  [ReferencedFrameOfReferenceUID] nvarchar(255),
  PRIMARY KEY ([ID], [StudyID])
)
GO

CREATE TABLE [DICOM].[RTStructureDose] (
  [ID] int,
  [RTStructID] int,
  [RTDoseID] int,
  [StructureName] nvarchar(255),
  [StructureVolume] nvarchar(255),
  [LocalStructureID] int,
  [GlobalStructureID] int,
  [TotalDoseGray] float,
  [DVHGy] nvarchar(25000),
  [DVHVpercent] nvarchar(25000),
  PRIMARY KEY ([ID], [RTStructID], [RTDoseID])
)
GO

CREATE TABLE [DICOM].[RTDoseSeries] (
  [ID] int,
  [StudyID] int,
  [ReferencedRTPlan] nvarchar(255),
  PRIMARY KEY ([ID], [StudyID])
)
GO

CREATE TABLE [DICOM].[Structures] (
  [ID] int,
  [Name] nvarchar(255),
  [NamingScheme] nvarchar(255)
)
GO

EXEC sp_addextendedproperty
@name = N'Column_Description',
@value = 'TG-263, RTOG, ...',
@level0type = N'Schema', @level0name = 'DICOM',
@level1type = N'Table',  @level1name = 'Structures',
@level2type = N'Column', @level2name = 'NamingScheme';
GO

ALTER TABLE [DICOM].[Patient] ADD FOREIGN KEY ([HelseforetakID]) REFERENCES [DICOM].[Institution] ([ID])
GO

ALTER TABLE [DICOM].[Study] ADD FOREIGN KEY ([PatientID]) REFERENCES [DICOM].[Patient] ([ID])
GO

ALTER TABLE [DICOM].[RTImageSeries] ADD FOREIGN KEY ([StudyID]) REFERENCES [DICOM].[Study] ([ID])
GO

ALTER TABLE [DICOM].[RTStructSeries] ADD FOREIGN KEY ([StudyID]) REFERENCES [DICOM].[Study] ([ID])
GO

ALTER TABLE [DICOM].[RTStructureDose] ADD FOREIGN KEY ([RTStructID]) REFERENCES [DICOM].[RTStructSeries] ([ID])
GO

ALTER TABLE [DICOM].[RTStructureDose] ADD FOREIGN KEY ([RTDoseID]) REFERENCES [DICOM].[RTDoseSeries] ([ID])
GO

ALTER TABLE [DICOM].[RTStructureDose] ADD FOREIGN KEY ([GlobalStructureID]) REFERENCES [DICOM].[Structures] ([ID])
GO

ALTER TABLE [DICOM].[RTDoseSeries] ADD FOREIGN KEY ([StudyID]) REFERENCES [DICOM].[Study] ([ID])
GO


CREATE SCHEMA [DICOM]
GO

CREATE TABLE [DICOM].[Institution] (
  [ID] int,
  [Name] nvarchar(255),
  [Location] nvarchar(255),
  PRIMARY KEY ([ID])
)
GO

CREATE TABLE [DICOM].[Patient] (
  [ID] int,
  [HelseforetakID] int,
  [name] nvarchar(255),
  [PID] nvarchar(255),
  [PrimaryTumorSite] nvarchar(255),
  PRIMARY KEY ([ID])
)
GO

CREATE TABLE [DICOM].[Study] (
  [ID] int,
  [PatientID] int,
  [StudyInstanceUID] nvarchar(255),
  [StudyTime] datetime,
  PRIMARY KEY ([ID], [PatientID], [StudyInstanceUID])
)
GO

CREATE TABLE [DICOM].[RTImageSeries] (
  [ID] int,
  [StudyID] int,
  [Modality] nvarchar(255),
  [SeriesInstanceUID] nvarchar(255),
  [SliceThickness] float,
  [Manufacturer] nvarchar(255),
  [ManufacturersModelName] nvarchar(255),
  [SeriesTime] datetime,
  [kVp] int,
  [mAs] int,
  PRIMARY KEY ([ID], [StudyID])
)
GO

CREATE TABLE [DICOM].[RTStructSeries] (
  [ID] int,
  [StudyID] int,
  [ReferencedFrameOfReferenceUID] nvarchar(255),
  PRIMARY KEY ([ID], [StudyID])
)
GO

CREATE TABLE [DICOM].[RTStructureDose] (
  [ID] int,
  [RTStructID] int,
  [RTDoseID] int,
  [StructureName] nvarchar(255),
  [StructureVolume] nvarchar(255),
  [LocalStructureID] int,
  [GlobalStructureID] int,
  [TotalDoseGray] float,
  [DVHGy] nvarchar(25000),
  [DVHVpercent] nvarchar(25000),
  PRIMARY KEY ([ID], [RTStructID], [RTDoseID])
)
GO

CREATE TABLE [DICOM].[RTDoseSeries] (
  [ID] int,
  [StudyID] int,
  [ReferencedRTPlan] nvarchar(255),
  PRIMARY KEY ([ID], [StudyID])
)
GO

CREATE TABLE [DICOM].[Structures] (
  [ID] int,
  [Name] nvarchar(255),
  [NamingScheme] nvarchar(255)
)
GO

EXEC sp_addextendedproperty
@name = N'Column_Description',
@value = 'TG-263, RTOG, ...',
@level0type = N'Schema', @level0name = 'DICOM',
@level1type = N'Table',  @level1name = 'Structures',
@level2type = N'Column', @level2name = 'NamingScheme';
GO

ALTER TABLE [DICOM].[Patient] ADD FOREIGN KEY ([HelseforetakID]) REFERENCES [DICOM].[Institution] ([ID])
GO

ALTER TABLE [DICOM].[Study] ADD FOREIGN KEY ([PatientID]) REFERENCES [DICOM].[Patient] ([ID])
GO

ALTER TABLE [DICOM].[RTImageSeries] ADD FOREIGN KEY ([StudyID]) REFERENCES [DICOM].[Study] ([ID])
GO

ALTER TABLE [DICOM].[RTStructSeries] ADD FOREIGN KEY ([StudyID]) REFERENCES [DICOM].[Study] ([ID])
GO

ALTER TABLE [DICOM].[RTStructureDose] ADD FOREIGN KEY ([RTStructID]) REFERENCES [DICOM].[RTStructSeries] ([ID])
GO

ALTER TABLE [DICOM].[RTStructureDose] ADD FOREIGN KEY ([RTDoseID]) REFERENCES [DICOM].[RTDoseSeries] ([ID])
GO

ALTER TABLE [DICOM].[RTStructureDose] ADD FOREIGN KEY ([GlobalStructureID]) REFERENCES [DICOM].[Structures] ([ID])
GO

ALTER TABLE [DICOM].[RTDoseSeries] ADD FOREIGN KEY ([StudyID]) REFERENCES [DICOM].[Study] ([ID])
GO
