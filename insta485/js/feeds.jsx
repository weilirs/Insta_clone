import React from 'react';
import PropTypes from 'prop-types';
import Post from './post';
import InfiniteScroll from 'react-infinite-scroll-component';

class Feed extends React.Component {
  /* Display number of image and post owner of a single post
   */

  constructor(props) {
    // Initialize mutable state
    super(props);
    this.state = { posts:[],next:'',page:0};
    this.fetchData = this.fetchData.bind(this);
  }

  componentDidMount() {
    // This line automatically assigns this.props.url to the const variable url
    const { url } = this.props;

    // Call REST API to get the post's information
    fetch(url, { credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        this.setState({
          posts:data.results,
          next:data.next
        });
      })
      .catch((error) => console.log(error));
  }

   fetchData(){
     this.setState({page:this.state.page+1});
     const { url_fetch } = "http://localhost:8000/api/v1/p/?postid_lte=1";
     fetch(url_fetch, { credentials: 'same-origin' })
     .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        this.setState({
          posts:this.state.posts.concat(data.results),
          next:data.next
        });
      })
      .catch((error) => console.log(error));
   }
  render() {
    // This line automatically assigns this.state.imgUrl to the const variable imgUrl
    // and this.state.owner to the const variable owner



    return (
      <div className="Feed">
        <InfiniteScroll
  dataLength={this.state.posts.length} //This is important field to render the next data
  next={this.fetchData}
  hasMore={true}
  loader={<h4>Loading...</h4>}
  endMessage={
    <p style={{ textAlign: 'center' }}>
      <b>Yay! You have seen it all</b>
    </p>
  }
  >
        {this.state.posts.map(post => (<Post key={post.postid} url={post.url} /> ))}
        
  
</InfiniteScroll>
      </div>
    );
  }
}

  export default Feed;