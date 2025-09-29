from common import *
from ontology_populator.implementations.simple.io import data_reader_implementation, data_writer_implementation
from ontology_populator.implementations.knime.knime_implementation import KnimeImplementation, KnimeDefaultFeature, KnimeBaseBundle
from ontology_populator.implementations.knime.knime_parameter import KnimeTextParameter, KnimeSpecificParameter, KnimeFactorParameter

knime_csv_reader_implementation = KnimeImplementation(
    name='KNime CSV Reader',
    base_implementation=data_reader_implementation,
    parameters=[
        KnimeTextParameter('path', 
                           base_parameter=next((param for param in data_reader_implementation.parameters.keys() if param.label == "Reader File"), None),
                           default_value='$$PATH$$', path='model/settings/file_selection/path'),
        KnimeSpecificParameter('location_present', XSD.string, default_value=True, path='model/settings/file_selection/path'),
        KnimeSpecificParameter('file_system_type', XSD.string, "LOCAL", path='model/settings/file_selection/path'),

        KnimeSpecificParameter('SettingsModelID', XSD.string, 'SMID_ReaderFileChooser',
                       path='model/settings/file_selection_Internals'),
        KnimeSpecificParameter("EnabledStatus", XSD.boolean, True,
                       path='model/settings/file_selection_Internals'),

        KnimeSpecificParameter("has_fs_port", XSD.boolean, False,
                       path='model/settings/file_selection/file_system_chooser__Internals'),
        KnimeSpecificParameter("overwritten_by_variable", XSD.boolean, False, 
                       path='model/settings/file_selection/file_system_chooser__Internals'),
        KnimeSpecificParameter("convenience_fs_category", XSD.string, 'LOCAL', 
                       path='model/settings/file_selection/file_system_chooser__Internals'),
        KnimeSpecificParameter("relative_to", XSD.string, 'knime.workflow', 
                       path='model/settings/file_selection/file_system_chooser__Internals'),
        KnimeSpecificParameter("mountpoint", XSD.string, 'LOCAL', 
                       path='model/settings/file_selection/file_system_chooser__Internals'),
        KnimeSpecificParameter("spaceId", XSD.string, '', 
                       path='model/settings/file_selection/file_system_chooser__Internals'),
        KnimeSpecificParameter("spaceName", XSD.string, '', 
                       path='model/settings/file_selection/file_system_chooser__Internals'),
        KnimeSpecificParameter("custom_url_timeout", XSD.integer, 1000,
                       path='model/settings/file_selection/file_system_chooser__Internals'),
        KnimeSpecificParameter("connected_fs", XSD.boolean, True,
                       path='model/settings/file_selection/file_system_chooser__Internals'),

        KnimeSpecificParameter("has_column_header", XSD.boolean, True, path='model/settings'),
        KnimeSpecificParameter("has_row_id", XSD.boolean, False, path='model/settings'),
        KnimeSpecificParameter("support_short_data_rows", XSD.boolean, False,
                       path='model/settings'),
        KnimeSpecificParameter("skip_empty_data_rows", XSD.boolean, False, path='model/settings'),
        KnimeSpecificParameter("prepend_file_idx_to_row_id", XSD.boolean, False,
                       path='model/settings'),
        KnimeSpecificParameter("comment_char", XSD.string, '#', path='model/settings'),
        KnimeSpecificParameter("column_delimiter", XSD.string, ',', path='model/settings'),
        KnimeSpecificParameter("quote_char", XSD.string, '"', path='model/settings'),
        KnimeSpecificParameter("quote_escape_char", XSD.string, '"', path='model/settings'),
        KnimeSpecificParameter("use_line_break_row_delimiter", XSD.boolean, True, path='model/settings'),
        KnimeSpecificParameter("row_delimiter", XSD.string, '%%00013%%00010', path='model/settings'),
        KnimeSpecificParameter("autodetect_buffer_size", XSD.integer, 1048576,path='model/settings'),

        KnimeSpecificParameter("spec_merge_mode_Internals", XSD.string, 'UNION', path='model/advanced_settings'),
        KnimeSpecificParameter("fail_on_differing_specs", XSD.boolean, True, path='model/advanced_settings'),
        KnimeSpecificParameter("append_path_column_Internals", XSD.boolean, False, path='model/advanced_settings'),
        KnimeSpecificParameter("path_column_name_Internals", XSD.string, 'Path', path='model/advanced_settings'),
        KnimeSpecificParameter("limit_data_rows_scanned", XSD.boolean, True, path='model/advanced_settings'),
        KnimeSpecificParameter("max_data_rows_scanned", XSD.long, 10000, path='model/advanced_settings'),
        KnimeSpecificParameter("save_table_spec_config_Internals", XSD.boolean, True, path='model/advanced_settings'),
        KnimeSpecificParameter("limit_memory_per_column", XSD.boolean, True, path='model/advanced_settings'),
        KnimeSpecificParameter("maximum_number_of_columns", XSD.integer, 8192, path='model/advanced_settings'),
        KnimeSpecificParameter("quote_option", XSD.string, 'REMOVE_QUOTES_AND_TRIM', path='model/advanced_settings'),
        KnimeSpecificParameter("replace_empty_quotes_with_missing", XSD.boolean, True, path='model/advanced_settings'),
        KnimeSpecificParameter("thousands_separator", XSD.string, '%%00000', path='model/advanced_settings'),
        KnimeSpecificParameter("decimal_separator", XSD.string, '.', path='model/advanced_settings'),

        KnimeSpecificParameter("skip_lines", XSD.boolean, False, path='model/limit_rows'),
        KnimeSpecificParameter("number_of_lines_to_skip", XSD.long, 1, path='model/limit_rows'),
        KnimeSpecificParameter("skip_data_rows", XSD.boolean, False, path='model/limit_rows'),
        KnimeSpecificParameter("number_of_rows_to_skip", XSD.long, 1, path='model/limit_rows'),
        KnimeSpecificParameter("limit_data_rows", XSD.boolean, False, path='model/limit_rows'),
        KnimeSpecificParameter("max_rows", XSD.long, 50, path='model/limit_rows'),

        KnimeSpecificParameter("charset", XSD.string, None, path='model/encoding'),

        KnimeSpecificParameter('SMID_FilterMode', XSD.string,'SettingsModelID',path='model/settings/file_selection/filter_mode_Internals'),
        KnimeSpecificParameter('EnabledStatus', XSD.boolean, True, path='model/settings/file_selection/filter_mode_Internals'),

        KnimeSpecificParameter("filter_mode", XSD.string, 'FILE', path='model/settings/file_selection/filter_mode'),
        KnimeSpecificParameter("include_subfolders", XSD.boolean, False, path='model/settings/file_selection/filter_mode'),
        KnimeSpecificParameter("filter_files_extension", XSD.boolean, False, path='model/settings/file_selection/filter_mode/filter_options'),
        KnimeSpecificParameter("files_extension_expression", XSD.string, '', path='model/settings/file_selection/filter_mode/filter_options'),
        KnimeSpecificParameter("files_extension_case_sensitive", XSD.boolean, False, path='model/settings/file_selection/filter_mode/filter_options'),
        KnimeSpecificParameter("filter_files_name", XSD.boolean, False, path='model/settings/file_selection/filter_mode/filter_options'),
        KnimeSpecificParameter("files_name_expression", XSD.string, '*', path='model/settings/file_selection/filter_mode/filter_options'),
        KnimeSpecificParameter("files_name_case_sensitive", XSD.boolean, False, path='model/settings/file_selection/filter_mode/filter_options'),
        KnimeSpecificParameter("files_name_filter_type", XSD.string, 'WILDCARD', path='model/settings/file_selection/filter_mode/filter_options'),
        KnimeSpecificParameter("include_hidden_files", XSD.boolean, False, path='model/settings/file_selection/filter_mode/filter_options'),
        KnimeSpecificParameter("include_special_files", XSD.boolean, True, path='model/settings/file_selection/filter_mode/filter_options'),
        KnimeSpecificParameter("filter_folders_name", XSD.boolean, False, path='model/settings/file_selection/filter_mode/filter_options'),
        KnimeSpecificParameter("folders_name_expression", XSD.string, '*', path='model/settings/file_selection/filter_mode/filter_options'),
        KnimeSpecificParameter("folders_name_case_sensitive", XSD.boolean, False, path='model/settings/file_selection/filter_mode/filter_options'),
        KnimeSpecificParameter("folders_name_filter_type", XSD.string, 'WILDCARD', path='model/settings/file_selection/filter_mode/filter_options'),
        KnimeSpecificParameter("include_hidden_folders", XSD.boolean, False, path='model/settings/file_selection/filter_mode/filter_options'),
        KnimeSpecificParameter("follow_links", XSD.boolean, True, path='model/settings/file_selection/filter_mode/filter_options'),
        
        KnimeFactorParameter("Format", levels={'CSV':'CSV'},
                    base_parameter=next((param for param in data_reader_implementation.parameters.keys() if param.label == 'Format'), None),
                    default_value='CSV', path=None),

    ],
    knime_node_factory = 'org.knime.base.node.io.filehandling.csv.reader.CSVTableReaderNodeFactory',
    knime_bundle = KnimeBaseBundle,
    knime_feature = KnimeDefaultFeature
)

knime_csv_writer_implementation = KnimeImplementation(
    name='KNIME CSV Writer',
    base_implementation=data_writer_implementation,
    parameters=[
        KnimeTextParameter('path',
                           base_parameter=next((param for param in data_writer_implementation.parameters.keys() if param.label == "Output path"), None), 
                           default_value=r"./output.csv", path='model/settings/file_chooser_settings/path'),

        KnimeSpecificParameter('location_present', XSD.boolean, True, path='model/settings/file_chooser_settings/path'),
        KnimeSpecificParameter('file_system_type', XSD.string, "LOCAL",path='model/settings/file_chooser_settings/path'),

        KnimeSpecificParameter('create_missing_folders', XSD.boolean, True, path='model/settings/file_chooser_settings'),
        KnimeSpecificParameter('if_path_exists', XSD.string, 'fail', path='model/settings/file_chooser_settings'),

        KnimeSpecificParameter("SettingsModelID", XSD.string, 'SMID_WriterFileChooser', path='model/settings/file_chooser_settings_Internals'),
        KnimeSpecificParameter("EnabledStatus", XSD.boolean, True, path='model/settings/file_chooser_settings_Internals'),

        KnimeSpecificParameter("has_fs_port", XSD.boolean, False, path='model/settings/file_chooser_settings/file_system_chooser__Internals'),
        KnimeSpecificParameter("overwritten_by_variable", XSD.boolean, False, path='model/settings/file_chooser_settings/file_system_chooser__Internals'),
        KnimeSpecificParameter("convenience_fs_category", XSD.string, 'LOCAL', path='model/settings/file_chooser_settings/file_system_chooser__Internals'),
        KnimeSpecificParameter("relative_to", XSD.string, 'knime.workflow.data', path='model/settings/file_chooser_settings/file_system_chooser__Internals'),
        KnimeSpecificParameter("mountpoint", XSD.string, 'LOCAL', path='model/settings/file_chooser_settings/file_system_chooser__Internals'),
        KnimeSpecificParameter("spaceId", XSD.string, '', path='model/settings/file_chooser_settings/file_system_chooser__Internals'),
        KnimeSpecificParameter("spaceName", XSD.string, '', path='model/settings/file_chooser_settings/file_system_chooser__Internals'),
        KnimeSpecificParameter("custom_url_timeout", XSD.integer, 1000, path='model/settings/file_chooser_settings/file_system_chooser__Internals'),
        KnimeSpecificParameter("connected_fs", XSD.boolean, True, path='model/settings/file_chooser_settings/file_system_chooser__Internals'),

        KnimeSpecificParameter("SettingsModelID", XSD.string, 'SMID_FilterMode', path='model/settings/file_chooser_settings/filter_mode_Internals'),
        KnimeSpecificParameter("EnabledStatus", XSD.boolean, True, path='model/settings/file_chooser_settings/filter_mode_Internals'),

        KnimeSpecificParameter('column_delimiter', XSD.string, ',', path='model/settings'),
        KnimeSpecificParameter('row_delimeter', XSD.string, None, path='model/settings'),
        KnimeSpecificParameter('quote_char', cb.term('char'), '"', path='model/settings'),
        KnimeSpecificParameter('quote_escape_char', cb.term('char'), '"', path='model/settings'),
        KnimeSpecificParameter('write_column_header', XSD.boolean, True, path='model/settings'),
        KnimeSpecificParameter('skip_column_header_on_append', XSD.boolean, False, path='model/settings'),
        KnimeSpecificParameter('write_row_header', XSD.boolean, False, path='model/settings'),

        KnimeSpecificParameter('missing_value_pattern', XSD.string, '', path='model/advanced_settings'),
        KnimeSpecificParameter('compress_with_gzip', XSD.boolean, False, path='model/advanced_settings'),
        KnimeSpecificParameter('quote_mode', XSD.string, "STRINGS_ONLY", path='model/advanced_settings'),
        KnimeSpecificParameter('separator_replacement', XSD.string, '', path='model/advanced_settings'),
        KnimeSpecificParameter('decimal_separator', cb.term('char'), '.', path='model/advanced_settings'),
        KnimeSpecificParameter('use_scientific_format', XSD.boolean, False, path='model/advanced_settings'),
        KnimeSpecificParameter('keep_trailing_zero_in_decimals', XSD.boolean, False, path='model/advanced_settings'),

        KnimeSpecificParameter('comment_line_marker', XSD.string, '#', path='model/comment_header_settings'),
        KnimeSpecificParameter('comment_indentation', XSD.string, '%%00009', path='model/comment_header_settings'),
        KnimeSpecificParameter('add_time_to_comment', XSD.boolean, False, path='model/comment_header_settings'),
        KnimeSpecificParameter('add_user_to_comment', XSD.boolean, False, path='model/comment_header_settings'),
        KnimeSpecificParameter('add_table_name_to_comment', XSD.boolean, False, path='model/comment_header_settings'),
        KnimeSpecificParameter('add_custom_text_to_comment', XSD.boolean, False, path='model/comment_header_settings'),
        KnimeSpecificParameter('custom_comment_text', XSD.string, '', path='model/comment_header_settings'),

        KnimeSpecificParameter('character_set', XSD.string, 'windows-1252', path='model/encoding'),
    ],
    knime_node_factory = 'org.knime.base.node.io.filehandling.csv.writer.CSVWriter2NodeFactory',
    knime_bundle = KnimeBaseBundle,
    knime_feature = KnimeDefaultFeature
)

"""
csv_writer_local_component = Component(
    name='CSV Local writer',
    implementation=csv_writer_implementation,
    transformations=[],
    overriden_parameters=[
        ParameterSpecification(next((param for param in csv_writer_implementation.parameters.keys() if param.knime_key == 'location_present'), None), True),
        ParameterSpecification(next((param for param in csv_writer_implementation.parameters.keys() if param.knime_key == 'file_system_type'), None), "LOCAL")
    ],
    exposed_parameters=[
        next((param for param in csv_writer_implementation.parameters.keys() if param.knime_key == 'path'), None),
        next((param for param in csv_writer_implementation.parameters.keys() if param.knime_key == 'create_missing_folders'), None),
        next((param for param in csv_writer_implementation.parameters.keys() if param.knime_key == 'if_path_exists'), None),
        next((param for param in csv_writer_implementation.parameters.keys() if param.knime_key == 'column_delimiter'), None),
        next((param for param in csv_writer_implementation.parameters.keys() if param.knime_key == 'row_delimiter'), None),
        next((param for param in csv_writer_implementation.parameters.keys() if param.knime_key == 'quote_char'), None),
        next((param for param in csv_writer_implementation.parameters.keys() if param.knime_key == 'quote_escape_char'), None),
        next((param for param in csv_writer_implementation.parameters.keys() if param.knime_key == 'write_column_header'), None),
        next((param for param in csv_writer_implementation.parameters.keys() if param.knime_key == 'skip_column_header_on_append'), None),
        next((param for param in csv_writer_implementation.parameters.keys() if param.knime_key == 'write_row_header'), None),
    ]

)
"""
