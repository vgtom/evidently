import json

from pandas import DataFrame

from evidently import ColumnMapping
from evidently.analyzers.num_target_drift_analyzer import NumTargetDriftAnalyzer
from evidently.options import DataDriftOptions, OptionsProvider
from evidently.model_profile.sections.num_target_drift_profile_section import NumTargetDriftProfileSection
from evidently.utils import NumpyEncoder


def test_num_target_drift_profile_section_empty_results():
    profile_section = NumTargetDriftProfileSection()
    assert profile_section.analyzers() == [NumTargetDriftAnalyzer]
    assert profile_section.part_id() == 'num_target_drift'

    empty_result = profile_section.get_results()
    assert empty_result is None


def test_num_target_drift_profile_section_with_target_only():
    # prepare calculated data
    options_provider: OptionsProvider = OptionsProvider()
    options_provider.add(DataDriftOptions())
    data_drift_analyzer = NumTargetDriftAnalyzer()
    data_drift_analyzer.options_provider = options_provider
    test_data = DataFrame({
        'my_num_data': [1, 2, 3, 4],
    })
    data_columns = ColumnMapping(target='my_num_data')
    results = data_drift_analyzer.calculate(test_data[:2], test_data, data_columns)
    analyzers_results = {NumTargetDriftAnalyzer: results}

    # create the section with the calculated data
    data_drift_profile_section = NumTargetDriftProfileSection()
    data_drift_profile_section.calculate(test_data[:2], test_data, data_columns, analyzers_results)
    data_drift_profile_section_result = data_drift_profile_section.get_results()
    assert 'name' in data_drift_profile_section_result
    assert data_drift_profile_section_result['name'] == 'num_target_drift'
    assert 'datetime' in data_drift_profile_section_result
    assert isinstance(data_drift_profile_section_result['datetime'], str)
    assert 'data' in data_drift_profile_section_result
    assert isinstance(data_drift_profile_section_result['data'], dict)

    result_data = data_drift_profile_section_result['data']

    assert 'cat_feature_names' in result_data
    assert result_data['cat_feature_names'] == []
    assert 'num_feature_names' in result_data
    assert result_data['num_feature_names'] == []
    assert 'target_names' in result_data
    assert result_data['target_names'] is None
    assert 'utility_columns' in result_data
    assert 'metrics' in result_data
    assert 'target_name' in result_data['metrics']
    assert result_data['metrics']['target_name'] == 'my_num_data'
    assert 'target_type' in result_data['metrics']
    assert result_data['metrics']['target_type'] == 'num'
    assert 'target_drift' in result_data['metrics']

    # check json serialization
    json.dumps(data_drift_profile_section_result, cls=NumpyEncoder)
