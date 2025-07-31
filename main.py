import faulthandler
faulthandler.enable()
from utils import read_video, save_video
from trackers import PlayerTracker, BallTracker
from drawers import(
    PlayerTracksDrawer,
    BallTracksDrawer,
    TeamBallControlDrawer,
    PassAndInterceptionsDrawer,
    CourtKeypointsDrawer,
    TacticalViewDrawer
)
from team_assigner import TeamAssigner
from ball_acquisition import BallAcquisitionDetector
from pass_and_interception_detector import PassAndInterceptionDetector
from court_keypoint_detector import CourtKeypointDetector
from tactical_view_converter import TacticalViewConverter

def main():
    # read video
    video_frames = read_video("input_videos/video_1.mp4")

    # initialize tracker
    player_tracker = PlayerTracker("models/player_detector_model.pt")
    ball_tracker = BallTracker("models/ball_detector_model.pt")

    # run tracker
    player_tracks = player_tracker.get_object_tracks(video_frames, read_from_stub=True, stub_path="stubs/player_track_stubs.pkl")
    ball_tracks = ball_tracker.get_object_tracks(video_frames, read_from_stub=True, stub_path="stubs/ball_track_stubs.pkl")

    # get court keypoints
    court_keypoint_detector = CourtKeypointDetector("models/court_keypoint_detector_model.pt")
    court_keypoints = court_keypoint_detector.get_court_keypoints(video_frames, read_from_stub=True, stub_path="stubs/court_keypoint_stubs.pkl")

    # remove wrong ball detections
    ball_tracks = ball_tracker.remove_wrong_detections(ball_tracks)

    # interpolate missing ball detections
    ball_tracks = ball_tracker.interpolate_ball_positions(ball_tracks)

    # assign players to teams
    team_assigner = TeamAssigner()
    player_assignment = team_assigner.get_player_teams_across_frames(
        video_frames, player_tracks, read_from_stub=True, stub_path="stubs/player_team_stubs.pkl"
    )

    # ball acquisition detection
    ball_acquisition_detector = BallAcquisitionDetector()
    ball_acquisition = ball_acquisition_detector.detect_ball_possession(player_tracks, ball_tracks)

    # detect pass and interception
    pass_and_interception_detector = PassAndInterceptionDetector()
    passes = pass_and_interception_detector.detect_passes(ball_acquisition, player_assignment)
    interceptions = pass_and_interception_detector.detect_interceptions(ball_acquisition, player_assignment)

    # convert to tactical view
    tactical_view_converter = TacticalViewConverter(court_image_path="./images/basketball_court.png")

    # initialize drawers
    player_tracks_drawer = PlayerTracksDrawer()
    ball_tracks_drawer = BallTracksDrawer()
    team_ball_control_drawer = TeamBallControlDrawer()
    pass_and_interceptions_drawer = PassAndInterceptionsDrawer()
    court_keypoints_drawer = CourtKeypointsDrawer()
    tactical_view_drawer = TacticalViewDrawer()

    # draw objects
    output_video_frames = player_tracks_drawer.draw(video_frames, player_tracks, player_assignment, ball_acquisition)
    output_video_frames = ball_tracks_drawer.draw(output_video_frames, ball_tracks)

    # draw team ball control
    output_video_frames = team_ball_control_drawer.draw(output_video_frames, player_assignment, ball_acquisition)

    # draw passes and interceptions
    output_video_frames = pass_and_interceptions_drawer.draw(output_video_frames, passes, interceptions)

    # draw court keypoints
    output_video_frames = court_keypoints_drawer.draw(output_video_frames, court_keypoints)

    # tactical view
    output_video_frames = tactical_view_drawer.draw(output_video_frames,
                                                    tactical_view_converter.court_image_path,
                                                    tactical_view_converter.width,
                                                    tactical_view_converter.height,
                                                    tactical_view_converter.key_points
                                                    )

    # save video    
    save_video(output_video_frames, "output_videos/output_video.avi")

if __name__ == "__main__":
    main()