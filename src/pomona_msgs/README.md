# pomona_msgs

Custom message / service / action package for Pomona. **Empty on day 1.**

When you add a `.msg`:

1. Create the file under `msg/`, e.g. `msg/PickTarget.msg`.
2. In `CMakeLists.txt`, uncomment the `rosidl_generate_interfaces` block
   and list the file in `MSG_FILES`.
3. Rebuild.

Same pattern for `srv/` and `action/`.
